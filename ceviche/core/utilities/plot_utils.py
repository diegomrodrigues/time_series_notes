import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from typing import Dict, Any, List, Optional
import json
import re
import textwrap
import subprocess
import tempfile
from pathlib import Path
import time


class PlotGenerationMixin:
    """Mixin class for generating plots from code blocks in content."""
    
    def generate_plots_from_code(self, content: str, task_config: Dict[str, Any], directory: Optional[Path] = None) -> str:
        """Orchestrates plot generation from code blocks in content."""
        print("\n🔍 Plot generation from code blocks")

        base_dir = self._get_base_directory(directory, task_config)
        images_dir = base_dir / "images"
        self._prepare_images_directory(images_dir)
        
        code_blocks = self._find_plot_code_blocks(content)
        
        return self._process_code_blocks(content, code_blocks, images_dir)

    def _get_base_directory(self, directory: Optional[Path], task_config: Dict[str, Any]) -> Path:
        """Determine the base directory for plot generation."""
        if directory:
            return directory
        return Path(task_config.get('directory', '.'))

    def _prepare_images_directory(self, images_dir: Path) -> None:
        """Ensure images directory exists."""
        images_dir.mkdir(exist_ok=True)

    def _find_plot_code_blocks(self, content: str) -> List[tuple[str, str]]:
        """Identify Python code blocks containing plotting code."""
        code_patterns = [
            r'```python\n(.*?)\n```',
            r'```py\n(.*?)\n```'
        ]
        
        plotting_keywords = ['plt.', 'matplotlib', 'seaborn', 'sns.']
        code_blocks = []
        
        for pattern in code_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                raw_code = match.group(1).strip()
                if any(keyword in raw_code for keyword in plotting_keywords):
                    code_blocks.append((match.group(0), raw_code))
        
        print(f"  - Found {len(code_blocks)} potential plotting code blocks")
            
        return code_blocks

    def _process_code_blocks(self, content: str, code_blocks: List[tuple[str, str]], images_dir: Path) -> str:
        """Process all identified code blocks to generate plots."""
        updated_content = content
        
        for i, (original_block, code) in enumerate(code_blocks, start=1):
            try:
                temp_path = self._create_temp_script(code, images_dir, i)
                success = self._execute_plot_script(temp_path, images_dir, i)
                
                if success:
                    plot_markdown = f'![Generated plot](./images/plot_{i}.png)'
                    updated_content = updated_content.replace(original_block, plot_markdown, 1)
                    
            except Exception as e:
                print(f"  ❌ Error processing code block: {str(e)}")
            finally:
                Path(temp_path).unlink(missing_ok=True)
                
        return updated_content

    def _create_temp_script(self, code: str, images_dir: Path, index: int) -> str:
        """Create temporary Python script with necessary imports and savefig."""
        imports = []
        if 'matplotlib' not in code:
            imports.append('import matplotlib.pyplot as plt')
        if 'numpy' in code and 'import numpy' not in code:
            imports.append('import numpy as np')
        if 'seaborn' in code or 'sns.' in code:
            imports.append('import seaborn as sns')

        final_code = '\n'.join([
            *imports,
            code.replace('plt.show()', '').strip(),
            f'plt.savefig("plot_{index}.png", bbox_inches="tight")',
            'plt.close()'
        ])

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(final_code)
            print(f"  - Created temporary file: {f.name}")
            return f.name

    def _execute_plot_script(self, script_path: str, images_dir: Path, index: int) -> bool:
        """Execute Python script and validate plot generation."""
        try:
            result = subprocess.run(
                ['python', script_path],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=images_dir
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Script failed with exit code {result.returncode}")
                
            if not (images_dir / f"plot_{index}.png").exists():
                raise FileNotFoundError(f"plot_{index}.png not generated")
                
            print(f"  ✓ Successfully generated plot_{index}.png")
            return True
            
        except subprocess.TimeoutExpired:
            print("  ⚠️ Plot generation timed out")
            return False
        except Exception as e:
            print(f"  ⚠️ Plot generation failed: {str(e)}")
            return False