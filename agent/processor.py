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
                    
                    # Add plot generation if configured
                    if task_config.get('generate_plots', False):
                        result = self._generate_plots_from_code(extracted_json, task_config)
                    
                    return extracted_json
                else:
                    if self.debug:
                        print("  ❌ JSON extraction failed")
                    print("⚠️ JSON extraction failed.")
                    return None
                    
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
        """Extract JSON from text response using multiple fallback strategies."""
        if self.debug:
            print("\n🔍 DEBUG: JSON extraction")
            print(f"  - Input text length: {len(text)}")
        
        # Strategy 1: Look for ```json blocks
        json_block = re.search(
            r"```(?:json)?\s*([\{\[].*?[\}\]])\s*```", 
            text, 
            re.DOTALL | re.IGNORECASE
        )
        if json_block:
            if self.debug:
                print("  - Found JSON code block")
            try:
                json_str = json_block.group(1).strip()
                json.loads(json_str)  # Validate JSON
                if self.debug:
                    print("  ✔️ Successfully parsed JSON from code block")
                return json_str
            except json.JSONDecodeError:
                if self.debug:
                    print("  ⚠️ Found JSON block but failed to parse")
        
        # Strategy 2: Look for any JSON structures
        if self.debug:
            print("  - Searching for JSON structures")
        
        json_candidates = re.finditer(
            r'(?:(?<=\n)|^)([\[{](?:[^\[\]{}]|(?1))*[\]}])',
            text, 
            re.DOTALL
        )
        
        for i, match in enumerate(json_candidates):
            if self.debug:
                print(f"  - Checking candidate {i + 1}")
            try:
                candidate = match.group(1).strip()
                # Validate JSON structure
                if (candidate.startswith(('{', '[')) and 
                    candidate.endswith(('}', ']')) and
                    candidate.count('{') == candidate.count('}') and
                    candidate.count('[') == candidate.count(']')):
                    
                    json.loads(candidate)
                    if self.debug:
                        print(f"  ✔️ Found valid JSON in candidate {i + 1}")
                    return candidate
            except json.JSONDecodeError:
                if self.debug:
                    print(f"  ⚠️ Candidate {i + 1} is not valid JSON")
                continue

        if self.debug:
            print("  ❌ No valid JSON found in response")
        print("⚠️ No valid JSON found in response")
        return None

    def _generate_plots_from_code(self, content: str, task_config: Dict[str, Any]) -> str:
        """Extract and execute Python code blocks to generate plots."""
        if self.debug:
            print("\n🔍 DEBUG: Plot generation from code blocks")
        
        # Create images directory if needed
        images_dir = Path(task_config.get('directory', '.')) / "images"
        images_dir.mkdir(exist_ok=True)
        
        # Find all Python code blocks
        code_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
        
        for i, code in enumerate(code_blocks):
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
                    # Redirect plots to file instead of showing
                    modified_code = code.replace('plt.show()', 'plt.savefig(f"{images_dir}/plot_{i}.png")')
                    f.write(modified_code)
                    temp_path = f.name
                
                # Execute in isolated process
                result = subprocess.run(
                    ['python', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=images_dir
                )
                
                if result.returncode == 0 and (images_dir / f"plot_{i}.png").exists():
                    # Replace code block with image reference
                    content = content.replace(
                        f'```python\n{code}\n```',
                        f'![Generated plot](./images/plot_{i}.png)',
                        1
                    )
                    
                if self.debug:
                    print(f"  - Processed code block {i+1}, return code: {result.returncode}")
                
            except Exception as e:
                if self.debug:
                    print(f"  ⚠️ Error processing code block {i+1}: {str(e)}")
                continue
            finally:
                Path(temp_path).unlink(missing_ok=True)
        
        return content
