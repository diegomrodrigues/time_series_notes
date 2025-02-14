from pathlib import Path
from typing import List, Optional, Dict, Any
import json
from concurrent.futures import ThreadPoolExecutor
from ceviche.core.agent import Agent
from ceviche.core.context import Context
from ceviche.workflows.create_topics import CreateTopicsWorkflow
from ceviche.workflows.generate_initial_draft import GenerateInitialDraftWorkflow
from ceviche.workflows.enhance_draft import EnhanceDraftWorkflow
from ceviche.workflows.generate_filename import GenerateFilenameWorkflow

class DirectoryProcessorAgent(Agent):
    """Handles the processing of directories and their contents."""

    def __init__(self, debug: bool = False):
        super().__init__(debug)
        self.debug = debug

    def pre_execution(self, ctx: Context, args: Dict[str, Any]):
        """Prepare the context before processing."""
        if self.debug:
            print("DirectoryProcessor: pre_execution")
        ctx["context"] = args.get("context", "General Context")
        ctx["debug"] = self.debug

    def execute(self, ctx: Context, args: Dict[str, Any]) -> Any:
        """Process a directory: create topics, generate drafts, and enhance."""
        directory = Path(args["directory"])
        max_workers = args.get("max_workers", 4)  # Default to 4 workers
        max_previous_topics = args.get("max_previous_topics", 3)

        try:
            # Create Topics
            topics = self._create_topics(directory, ctx, args)

            # Process Sections (using ThreadPoolExecutor for parallel processing)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for section in topics["topics"]:
                    future = executor.submit(
                        self._process_section,
                        ctx,
                        args,
                        directory,
                        section["topic"],
                        section["sub_topics"],
                        max_previous_topics,
                    )
                    futures.append(future)
                
                # Wait for all futures to complete before continuing
                for future in futures:
                    future.result()
            
        except Exception as e:
            print(f"❌ Failed to process directory: {directory}")
            print(f"Error: {str(e)}")
            raise

    def _create_topics(self, directory: Path, ctx: Context, args: Dict[str, Any]):
        """Creates topics for the given directory."""
        if self.debug:
            print("Creating topics...")

        topics_file = directory / "topics.json"
        
        # Check for existing topics.json
        if topics_file.exists():
            if self.debug:
                print(f"Loading existing topics from {topics_file}")
            return json.loads(topics_file.read_text())

        # Create new topics if file doesn't exist
        create_topics_workflow = self.get_workflow("create_topics", ctx, args)
        create_topics_args = {
            "directory": str(directory),
            "content": ctx["context"],
        }
        topics = create_topics_workflow.run(ctx, create_topics_args)

        # Save generated topics to JSON file
        topics_file.write_text(json.dumps(topics, indent=2))
        if self.debug:
            print(f"Saved topics to {topics_file}")
            print(f"Topics created: {topics}")
        
        return topics

    def _process_section(
        self,
        ctx: Context,
        args: Dict[str, Any],
        directory: Path,
        section_name: str,
        subtopics: List[str],
        max_previous_topics: int,
    ):
        """Processes a single section within the directory."""
        if self.debug:
            print(f"Processing section: {section_name}")

        section_dir = directory / section_name
        section_dir.mkdir(parents=True, exist_ok=True)

        previous_topics: List[Dict[str, Any]] = []

        for topic_name in subtopics:  # Iterate through subtopics
            self._process_topic(
                ctx,
                args,
                section_dir,
                section_name,
                topic_name,
                previous_topics,
                max_previous_topics,
            )
            # Add to previous_topics list (for context in subsequent iterations)
            if len(previous_topics) >= max_previous_topics:
                previous_topics.pop(0)  # Keep the list to max_previous_topics
            previous_topics.append({"topic": topic_name, "content": ctx["current_topic_content"]})

    def _process_topic(
        self,
        ctx: Context,
        args: Dict[str, Any],
        section_dir: Path,
        section_name: str,
        topic_name: str,
        previous_topics: List[Dict[str, Any]],
        max_previous_topics: int,
    ):
        """Generates and enhances a draft for a single topic."""
        if self.debug:
            print(f"Processing topic: {topic_name}")

        # Generate Initial Draft
        draft_workflow = self.get_workflow("generate_initial_draft", ctx, args)
        draft_args = {
            "directory": str(section_dir),
            "section_name": section_name,
            "topic": topic_name,
            "context": self.build_context_string(previous_topics),  # Pass context string
        }
        initial_draft = draft_workflow.run(ctx, draft_args)
        ctx["current_topic_content"] = initial_draft # Store for use by previous_topics

        # Enhance Draft
        enhance_workflow = self.get_workflow("enhance_draft", ctx, args)
        enhance_args = {"content": initial_draft, "directory": str(section_dir)}
        enhanced_draft = enhance_workflow.run(ctx, enhance_args)

        # Generate Filename and Save
        filename_workflow = self.get_workflow("generate_filename", ctx, args)
        filename_args = {"topic": topic_name, "content": topic_name, "directory": str(section_dir)}
        filename, filepath = filename_workflow.run(ctx, filename_args)

        filepath.write_text(enhanced_draft, encoding="utf-8")
        print(f"✔️ Saved topic to: {filepath}")

    def build_context_string(self, previous_topics: List[Dict[str, Any]]) -> str:
        """Builds a context string from previous topics."""
        context_parts = []
        for topic_result in previous_topics:
            context_parts.extend([
                f"--- START {topic_result['topic']} ---",
                topic_result['content'],
                f"--- END {topic_result['topic']} ---",
            ])
        return "\n".join(context_parts)

    def post_execution(self, ctx: Context, args: Dict[str, Any], result: Any):
        """Clean up or finalize after processing."""
        if self.debug:
            print("DirectoryProcessor: post_execution")
        # Add any post-processing steps here, if needed.