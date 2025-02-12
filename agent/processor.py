import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime
import json
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from .utils import retry_on_error
import re  # Ensure the re module is imported
import subprocess
import tempfile

class TaskProcessor:
    """Handles communication with the Gemini API for processing tasks."""
    
    def __init__(self, api_key: str, debug: bool = False):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self._configure_safety_settings()
        self.debug = True
    
    def _configure_safety_settings(self):
        """Configure default safety settings for the model."""
        self.SAFETY_SETTINGS = {
            category: HarmBlockThreshold.BLOCK_NONE 
            for category in [
                HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                HarmCategory.HARM_CATEGORY_HARASSMENT,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT
            ]
        }

    def create_model(self, task_config: Dict[str, Any]) -> genai.GenerativeModel:
        """Create a Gemini model with specific configuration."""
        model_config = self._get_model_config(task_config)
        
        return genai.GenerativeModel(
            model_name=task_config.get("model_name", "gemini-2.0-flash-exp"),
            generation_config=model_config,
            safety_settings=self.SAFETY_SETTINGS,
            system_instruction=task_config["system_instruction"]
        )
    
    def _get_model_config(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get model configuration from task config with defaults."""
        return {
            "temperature": task_config.get("temperature", 1),
            "top_p": task_config.get("top_p", 0.95),
            "top_k": task_config.get("top_k", 40),
            "max_output_tokens": task_config.get("max_output_tokens", 8192),
            "response_mime_type": task_config.get("response_mime_type", "text/plain")
        }

    @retry_on_error(max_retries=3)
    def upload_file(self, file_path: str, mime_type: Optional[str] = None) -> Any:
        """Upload a file to Gemini."""
        print(f"Uploading file: {file_path}")
        file = genai.upload_file(file_path, mime_type=mime_type)
        print(f"✓ Uploaded file '{file.display_name}' as: {file.uri}")
        return file

    def wait_for_files_active(self, files: List[Any]) -> None:
        """Wait for uploaded files to be processed."""
        print("Waiting for file processing...")
        for name in (file.name for file in files):
            file = genai.get_file(name)
            while file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(10)
                file = genai.get_file(name)
            if file.state.name != "ACTIVE":
                raise Exception(f"File {file.name} failed to process")
        print("...all files ready")

    def process_task(
        self,
        task_name: str,
        task_config: Dict[str, Any],
        content: str,
        expect_json: bool = False,
        extract_json: bool = False,
        files: Optional[List[Any]] = None
    ) -> Optional[str]:
        """Process a single task using the Gemini API."""
        print(f"Processing task: {task_name}")
        
        if self.debug:
            print("\n🔍 DEBUG: Processing task")
            print(f"  - Task name: {task_name}")
            print(f"  - Expect JSON: {expect_json}")
            print(f"  - Extract JSON: {extract_json}")
            print(f"  - Files attached: {bool(files)}")
            print(f"  - Content length: {len(content)}")
            print(f"  - Model config: {task_config.get('model_name', 'gemini-2.0-pro-exp-02-05')}")
        
        model = self.create_model(task_config)
        chat = self._initialize_chat(model, files)
        user_content, success = self._prepare_user_content(content, task_config)
        
        if not success:
            print("  - User content preparation not successfull")
            return content

        if self.debug:
            print("  - Chat initialized")
            print(f"  - Prepared content length: {len(user_content)}")

        try:
            if self.debug:
                print("  - Sending message to model...")
            
            response = chat.send_message(user_content)
            result = response.text

            if self.debug:
                print(f"  - Response received: {bool(result)}")
                print(result[:500])
                if result:
                    print(f"  - Response length: {len(result)}")
            
            if result and extract_json:
                if self.debug:
                    print("  - Attempting JSON extraction")
                
                extracted_json = self._extract_json(result)
                if extracted_json:
                    if self.debug:
                        print("  ✔️ JSON extraction successful")
                        print(f"  - JSON length: {len(extracted_json)}")
                    print("✓ JSON extraction succeed")
                    
                    
                    return extracted_json
                else:
                    if self.debug:
                        print("  ❌ JSON extraction failed")
                    print("⚠️ JSON extraction failed.")
                    return None

            # Add plot generation if configured
            if result and task_config.get('generate_plots', False):
                result = self._generate_plots_from_code(result, task_config)

            return result
            
        except Exception as e:
            if self.debug:
                print(f"  ❌ Task processing error: {str(e)}")
            return None
    
    def _initialize_chat(self, model: genai.GenerativeModel, 
                        files: Optional[List[Any]] = None) -> Any:
        """Initialize chat with optional file history."""
        if not files:
            return model.start_chat()
            
        history = [{"role": "user", "parts": [file]} for file in files]
        return model.start_chat(history=history)
    
    def _prepare_user_content(self, content: str, task_config: Dict[str, Any]) -> str:
        """Prepare the user content for the model."""
        if task_config.get("user_message"):
            user_message = task_config["user_message"]
            
            # Handle image content injection
            if "{images_content}" in user_message:
                try:
                    dir_line = next(line for line in content.split('\n') 
                                  if line.startswith("DIRECTORY_PLACEHOLDER ="))
                    directory = Path(dir_line.split('=', 1)[1].strip())
                    images_file = directory / "images.md"
                    
                    if images_file.exists():
                        images_content = images_file.read_text(encoding='utf-8')
                    else:
                        print(f"No images.md available in directory: {directory}")
                        return "No images available", False
                        
                    user_message = user_message.replace("{images_content}", images_content)
                except (StopIteration, IndexError):
                    user_message = user_message.replace("{images_content}", "No directory context available")
            
            return user_message.replace("{content}", content), True
        
        return content, True
    
    def _handle_response(self, response: Any, task_name: str) -> Optional[str]:
        """Handle the model's response."""
        return response.text
 
    def _extract_json(self, text: str) -> Optional[str]:
        """Enhanced JSON extraction with multiple fallback strategies."""
        strategies = [
            self._extract_json_via_code_block,
            self._extract_json_via_bracket_matching,
            self._extract_json_via_repair
        ]
        
        for strategy in strategies:
            result = strategy(text)
            if result and self._validate_json(result):
                return result
            
        return None

    def _extract_json_via_repair(self, text: str) -> Optional[str]:
        """Attempt to repair malformed JSON."""        
        # Simple bracket balancing
        balanced = self._balance_json_brackets(text)
        if balanced != text and self._validate_json(balanced):
            return balanced
        
        return None

    def _validate_json(self, json_str: str) -> bool:
        """Thorough JSON validation with error reporting."""
        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError as e:
            if self.debug:
                print(f"JSON Validation Failed: {e.msg}")
                print(f"Error position: {e.pos}")
                print(f"Invalid JSON snippet: {json_str[e.pos-50:e.pos+50]}")
            return False

    def _generate_plots_from_code(self, content: str, task_config: Dict[str, Any]) -> str:
        """Extract and execute Python code blocks to generate plots."""
        if self.debug:
            print("\n🔍 DEBUG: Plot generation from code blocks")
        
        # Create images directory if needed
        images_dir = Path(task_config.get('directory', '.')) / "images"
        images_dir.mkdir(exist_ok=True)
        
        # Get the next available plot index
        existing_plots = [f.stem for f in images_dir.glob('plot_*.png')]
        next_index = max([int(name.split('_')[1]) for name in existing_plots], default=-1) + 1
        
        if self.debug:
            print(f"  - Images directory: {images_dir}")
            print(f"  - Next plot index starts at: {next_index}")
        
        # Find all Python code blocks with different possible formats
        code_patterns = [
            r'```python\n(.*?)\n```',           # Standard format
            r'```py\n(.*?)\n```'                # Alternative format
        ]
        
        code_blocks = []
        for pattern in code_patterns:
            blocks = re.finditer(pattern, content, re.DOTALL)
            for block in blocks:
                code = block.group(1).strip()
                # Only process blocks that seem to contain plotting code
                if any(keyword in code for keyword in ['plt.', 'matplotlib', 'seaborn', 'sns.']):
                    code_blocks.append((block.group(0), code))
        
        if self.debug:
            print(f"  - Found {len(code_blocks)} potential plotting code blocks")
        
        for i, (original_block, code) in enumerate(code_blocks, start=next_index):
            if self.debug:
                print(f"\n  Processing code block {i}:")
                print(f"  {'='*40}")
                print(f"  {code[:200]}...")
            
            try:
                # Create temporary file with necessary imports
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
                    # Add common imports if not present
                    imports = []
                    if 'matplotlib' not in code:
                        imports.append('import matplotlib.pyplot as plt')
                    if 'numpy' in code and 'numpy' not in imports:
                        imports.append('import numpy as np')
                    if 'seaborn' in code or 'sns.' in code:
                        imports.append('import seaborn as sns')
                    
                    # Modify the code to save instead of show
                    modified_code = '\n'.join(imports) + '\n\n' if imports else ''
                    modified_code += code.replace('plt.show()', '').strip()
                    modified_code += f'\nplt.savefig("plot_{i}.png")\nplt.close()'
                    
                    f.write(modified_code)
                    temp_path = f.name
                    
                    if self.debug:
                        print(f"  - Created temporary file: {temp_path}")
                        print("  - Modified code:")
                        print(f"  {modified_code[:200]}...")
                
                # Execute in isolated process
                if self.debug:
                    print("  - Executing code...")
                
                result = subprocess.run(
                    ['python', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=images_dir
                )
                
                if self.debug:
                    print(f"  - Execution return code: {result.returncode}")
                    if result.stderr:
                        print(f"  - Stderr: {result.stderr}")
                
                if result.returncode == 0 and (images_dir / f"plot_{i}.png").exists():
                    # Replace code block with image reference
                    content = content.replace(
                        original_block,
                        f'![Generated plot](./images/plot_{i}.png)',
                        1
                    )
                    if self.debug:
                        print(f"  ✓ Successfully generated plot_{i}.png")
                else:
                    if self.debug:
                        print("  ⚠️ Plot generation failed")
            
            except Exception as e:
                if self.debug:
                    print(f"  ❌ Error processing code block: {str(e)}")
                continue
            finally:
                Path(temp_path).unlink(missing_ok=True)
        
        return content

    def _extract_json_via_code_block(self, text: str) -> Optional[str]:
        """Extract JSON from markdown code blocks with multiple fallbacks."""
        code_block_patterns = [
            r'```json\n(.*?)\n```',  # Standard JSON code block
            r'```\n(.*?)\n```',      # Generic code block
            r'```.*?\n(.*?)\n```'    # Code block with language specifier
        ]
        
        for pattern in code_block_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                # Try all matches and return first valid JSON
                for match in matches:
                    cleaned = match.strip()
                    if self._validate_json(cleaned):
                        return cleaned
                    # Handle possible incomplete code blocks
                    if not cleaned.endswith(('}', ']')):
                        for end in ['}', ']']:
                            if end in text:
                                candidate = cleaned + text.split(match)[-1].split(end)[0] + end
                                if self._validate_json(candidate):
                                    return candidate
                # If no matches validate, try the longest candidate
                longest_candidate = max(matches, key=len).strip()
                balanced = self._balance_json_brackets(longest_candidate)
                if self._validate_json(balanced):
                    return balanced
        
        return None

    def _extract_json_via_bracket_matching(self, text: str) -> Optional[str]:
        """Find JSON structure through bracket matching with error recovery."""
        open_brackets = {'{': 0, '[': 0}
        close_brackets = {'}': '{', ']': '['}
        start_index = None
        bracket_stack = []
        
        for i, char in enumerate(text):
            if char in open_brackets:
                if not bracket_stack:
                    start_index = i
                bracket_stack.append(char)
                open_brackets[char] += 1
            elif char in close_brackets:
                if bracket_stack and bracket_stack[-1] == close_brackets[char]:
                    bracket_stack.pop()
                    open_brackets[close_brackets[char]] -= 1
                else:
                    # Mismatched closing bracket - reset tracking
                    start_index = None
                    bracket_stack = []
                    open_brackets = {k: 0 for k in open_brackets}
                
            # Check if we've balanced all brackets
            if not bracket_stack and start_index is not None:
                candidate = text[start_index:i+1]
                if self._validate_json(candidate):
                    return candidate
                # Attempt to fix common issues in the candidate
                fixed = self._sanitize_json(candidate)
                if self._validate_json(fixed):
                    return fixed
        
        # Fallback: Try to extract after first opening bracket
        first_open = max(text.find('{'), text.find('['))
        if first_open != -1:
            candidate = text[first_open:]
            balanced = self._balance_json_brackets(candidate)
            if self._validate_json(balanced):
                return balanced
            # Try progressively shorter substrings
            for end in range(len(candidate), first_open+1, -1):
                if self._validate_json(candidate[:end]):
                    return candidate[:end]
        
        return None

    def _balance_json_brackets(self, json_str: str) -> str:
        """Balance JSON brackets with stack-based approach."""
        stack = []
        balanced = []
        
        for char in json_str:
            if char in ['{', '[']:
                stack.append(char)
            elif char in ['}', ']']:
                if stack and ((char == '}' and stack[-1] == '{') or (char == ']' and stack[-1] == '[')):
                    stack.pop()
                else:
                    # Add missing opening bracket
                    missing = '{' if char == '}' else '['
                    balanced.append(missing)
                    stack.append(missing)
            balanced.append(char)
        
        # Add remaining missing closing brackets
        while stack:
            missing = stack.pop()
            balanced.append('}' if missing == '{' else ']')
        
        return ''.join(balanced)
