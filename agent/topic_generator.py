from pathlib import Path
from typing import List, Optional, Dict
from .chain import TaskChain, ChainStep
from .processor import TaskProcessor
import json
import re
from .utils import retry_on_error

class TopicGenerator:
    """Generates and manages hierarchical topic structures from PDF documents."""
    
    def __init__(self, processor: TaskProcessor, tasks_config: dict):
        self.processor = processor
        self.tasks_config = tasks_config
        self.checkpoint_dir = Path(".checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

    def _save_checkpoint(self, phase: str, directory: Path, data: str) -> None:
        """Save checkpoint data for a specific phase."""
        checkpoint_file = self.checkpoint_dir / f"{directory.name}_{phase}.json"
        checkpoint_file.write_text(data, encoding='utf-8')
        print(f"📝 Checkpoint saved: {checkpoint_file}")

    def _load_checkpoint(self, phase: str, directory: Path) -> Optional[str]:
        """Load checkpoint data for a specific phase if it exists."""
        checkpoint_file = self.checkpoint_dir / f"{directory.name}_{phase}.json"
        if checkpoint_file.exists():
            print(f"📂 Loading checkpoint: {checkpoint_file}")
            return checkpoint_file.read_text()
        return None

    def generate(
        self,
        directory: Path,
        perspectives: Optional[List[str]] = None,
        num_topics: Optional[int] = None,
        jsons_per_perspective: int = 3,
        num_consolidation_steps: int = 2,
        resume_from: Optional[str] = None
    ) -> str:
        """
        Generate a structured topics hierarchy from PDF documents with checkpoint support.
        
        Args:
            directory: Path containing PDF files
            perspectives: List of perspective prompts for topic generation
            num_topics: Number of topic sets to generate if perspectives not provided
            jsons_per_perspective: Number of topic sets to generate per perspective
            num_consolidation_steps: Number of consolidation iterations
            resume_from: Optional phase to resume from ('initial_topics' or 'restructure')
        """
        self._validate_input(perspectives, num_topics)
        pdf_files = self._get_pdf_files(directory)
        
        # Phase 1: Generate initial topics
        if resume_from != 'restructure':
            checkpoint_data = self._load_checkpoint('initial_topics', directory)
            if checkpoint_data:
                perspective_results = json.loads(checkpoint_data)
            else:
                perspective_results = self._generate_initial_topics(
                    pdf_files=pdf_files,
                    perspectives=perspectives,
                    num_topics=num_topics or len(perspectives),
                    jsons_per_perspective=jsons_per_perspective
                )
                self._save_checkpoint('initial_topics', directory, 
                                    json.dumps(perspective_results))
        else:
            checkpoint_data = self._load_checkpoint('initial_topics', directory)
            if not checkpoint_data:
                raise ValueError("Cannot resume from restructure without initial topics checkpoint")
            perspective_results = json.loads(checkpoint_data)

        # Phase 2: Merge and restructure
        checkpoint_data = self._load_checkpoint('restructure', directory)
        if checkpoint_data:
            final_topics = checkpoint_data
        else:
            final_topics = self._process_and_restructure(
                directory=directory,
                perspective_results=perspective_results,
                num_consolidation_steps=num_consolidation_steps
            )
            self._save_checkpoint('restructure', directory, final_topics)

        # Save final results
        self._save_topics(directory, final_topics)
        return final_topics

    def _generate_initial_topics(
        self,
        pdf_files: List[Path],
        perspectives: Optional[List[str]],
        num_topics: int,
        jsons_per_perspective: int
    ) -> List[str]:
        """Generate initial topic sets with per-perspective checkpoints."""
        print("\n📚 Generating initial topic sets...")
        perspective_results = []
        
        for i in range(num_topics):
            perspective = perspectives[i] if perspectives else f"Perspective {i+1}"
            checkpoint_key = f"perspective_{i+1}"
            
            # Try to load perspective checkpoint
            checkpoint_data = self._load_checkpoint(checkpoint_key, pdf_files[0].parent)
            if checkpoint_data:
                perspective_results.append(checkpoint_data)
                print(f"✔️ Loaded perspective {i+1}/{num_topics} from checkpoint")
                continue

            print(f"\n🔍 Processing perspective {i+1}/{num_topics}: {perspective}")
            
            # Generate multiple topic sets for this perspective
            topic_sets = self._generate_topic_sets(
                pdf_files=pdf_files,
                perspective=perspective,
                perspective_index=i,
                num_sets=jsons_per_perspective
            )
            
            # Merge sets for this perspective
            merged_perspective = self._merge_topic_sets(topic_sets, i)
            perspective_results.append(merged_perspective)
            
            # Save perspective checkpoint
            self._save_checkpoint(checkpoint_key, pdf_files[0].parent, merged_perspective)
            print(f"✔️ Completed perspective {i+1}/{num_topics}")
            
        return perspective_results

    @retry_on_error(max_retries=3)
    def _generate_topic_sets(
        self,
        pdf_files: List[Path],
        perspective: str,
        perspective_index: int,
        num_sets: int
    ) -> List[str]:
        """Generate multiple topic sets for a single perspective."""
        topic_sets = []
        
        for set_index in range(num_sets):
            print(f"  → Generating set {set_index + 1}/{num_sets}")
            result = self._generate_single_set(
                pdf_files=pdf_files,
                perspective=perspective,
                perspective_index=perspective_index,
                set_index=set_index
            )
            if result:
                topic_sets.append(result)
        
        if not topic_sets:
            raise Exception(f"Failed to generate any valid topic sets for perspective {perspective_index+1}")
        return topic_sets

    def _generate_single_set(
        self,
        pdf_files: List[Path],
        perspective: str,
        perspective_index: int,
        set_index: int
    ) -> Optional[str]:
        """Generate a single set of topics using the task chain."""
        chain = TaskChain(self.processor, self.tasks_config, [
            ChainStep(
                name=f"Generate Topics Set {set_index+1} for Perspective {perspective_index+1}",
                tasks=["create_topics"],
                input_files=pdf_files,
                expect_json=True,
                max_iterations=3
            )
        ])
        
        result = chain.run(perspective)
        if not result:
            print(f"⚠️ Failed to generate set {set_index+1}")
        return result

    def _process_and_restructure(
        self,
        directory: Path,
        perspective_results: List[str],
        num_consolidation_steps: int
    ) -> str:
        """Merge all perspectives and restructure based on existing directory structure."""
        print("\n🔄 Merging and restructuring topics...")
        
        # Merge all perspective results
        merged_topics = self._merge_all_perspectives(perspective_results)
        
        # Restructure based on existing directory structure
        existing_dirs = self._get_existing_directories(directory)
        return self._restructure_topics(
            merged_topics=merged_topics,
            existing_dirs=existing_dirs,
            num_steps=num_consolidation_steps
        )

    def _merge_all_perspectives(self, perspective_results: List[str]) -> str:
        """Merge all perspective results into a single topic structure."""
        parsed_results = [json.loads(result) for result in perspective_results]
        merged = self._merge_topic_contents(parsed_results)
        return json.dumps(merged, indent=2, ensure_ascii=False)

    def _merge_topic_sets(self, topic_sets: List[str], perspective_index: int) -> str:
        """Merge multiple topic sets for a single perspective."""
        parsed_sets = [json.loads(topic_set) for topic_set in topic_sets]
        merged = self._merge_topic_contents(parsed_sets)
        return json.dumps(merged, indent=2, ensure_ascii=False)

    def _restructure_topics(
        self,
        merged_topics: str,
        existing_dirs: List[str],
        num_steps: int
    ) -> str:
        """Restructure topics based on existing directory structure."""
        context = json.dumps({"existing_directories": existing_dirs})
        
        chain = TaskChain(self.processor, self.tasks_config, [
            ChainStep(
                name=f"Consolidate Subtopics step {i}",
                tasks=["consolidate_subtopics"],
                expect_json=True,
                extract_json=True,
                max_iterations=5,
                use_previous_result=True,
                additional_context=context
            )
            for i in range(1, num_steps + 1)
        ])
        
        result = chain.run(merged_topics)
        if not result:
            raise Exception("Failed to restructure topics")
        return result

    def _validate_input(self, perspectives: Optional[List[str]], num_topics: Optional[int]):
        """Validate input parameters."""
        if perspectives is None and num_topics is None:
            raise ValueError("You should provide either perspectives or num_topics")

    def _get_pdf_files(self, directory: Path) -> List[Path]:
        """Get all PDF files in the directory."""
        return list(directory.glob("*.pdf"))

    def _get_existing_directories(self, directory: Path) -> List[str]:
        """Get existing directory names without numbering."""
        return [
            re.sub(r'^\d+\.\s*', '', d.name)
            for d in directory.iterdir() 
            if d.is_dir()
        ]

    def _merge_topic_contents(self, json_list: List[dict]) -> dict:
        """Merge multiple topic JSONs by combining topics and their sub-topics."""
        topic_map = {}
        
        # Process each JSON document
        for json_doc in json_list:
            for topic_item in json_doc.get('topics', []):
                topic = topic_item['topic']
                sub_topics = set(topic_item.get('sub_topics', []))
                
                if topic in topic_map:
                    # Merge sub-topics for existing topic
                    topic_map[topic].update(sub_topics)
                else:
                    # Create new topic entry
                    topic_map[topic] = sub_topics
        
        # Convert back to the required format
        merged_result = {
            "topics": [
                {
                    "topic": topic,
                    "sub_topics": sorted(list(sub_topics))
                }
                for topic, sub_topics in topic_map.items()
            ]
        }
        
        return merged_result

    def _save_topics(self, directory: Path, content: str) -> None:
        """Save the generated topics to a file."""
        output_file = directory / "topics.json"
        output_file.write_text(content, encoding='utf-8')
        print(f"✔️ Topics generated and saved to: {output_file}") 