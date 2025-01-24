import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime
import json
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from .utils import retry_on_error
import re  # Ensure the re module is imported

class TaskProcessor:
    """Handles communication with the Gemini API for processing tasks."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self._configure_safety_settings()
    
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

    def process_task(self, task_name: str, task_config: Dict[str, Any], 
                    content: str, expect_json: bool = False,
                    extract_json: bool = False,
                    files: Optional[List[Any]] = None) -> Optional[str]:
        """Process a single task using the Gemini API."""
        print(f"Processing task: {task_name}")
        
        model = self.create_model(task_config)
        chat = self._initialize_chat(model, files)
        user_content = self._prepare_user_content(content, task_config, expect_json)

        response = chat.send_message(user_content)
        result = self._handle_response(response, task_name)
        
        if result and extract_json:
            extracted_json = self._extract_json(result)
            if extracted_json:
                return extracted_json
            else:
                print("⚠️ JSON extraction failed.")
                return None
        return result
    
    def _initialize_chat(self, model: genai.GenerativeModel, 
                        files: Optional[List[Any]] = None) -> Any:
        """Initialize chat with optional file history."""
        if not files:
            return model.start_chat()
            
        history = [{"role": "user", "parts": [file]} for file in files]
        return model.start_chat(history=history)
    
    def _prepare_user_content(self, content: str, task_config: Dict[str, Any], 
                            expect_json: bool) -> str:
        """Prepare the user content for the model."""
        if expect_json:
            return (f"{content}\n\nContinue completing this JSON structure "
                   "exactly from its end. Do not repeat any previous content.")
        
        if task_config.get("user_message"):
            # Use replace instead of format for safer string handling
            user_message = task_config["user_message"]
            return user_message.replace("{content}", content)
    
        return content
    
    def _handle_response(self, response: Any, task_name: str) -> Optional[str]:
        """Handle the model's response."""
        if response.text:
            print(f"✓ Successfully completed task: {task_name}")
            return response.text
            
        print(f"❌ Failed to process task: {task_name}")
        return None

    def _extract_json(self, text: str) -> Optional[str]:
        """
        Extract JSON from text response using multiple fallback strategies.
        Returns the first valid JSON found or None if no valid JSON is found.
        """
        # Strategy 1: Look for ```json blocks
        json_block = re.search(r"```(?:json)?[\s\n]*(\{.*?\})[\s\n]*```", text, re.DOTALL | re.IGNORECASE)
        if json_block:
            try:
                json_str = json_block.group(1)
                json.loads(json_str)  # Validate JSON
                return json_str
            except json.JSONDecodeError:
                print("⚠️ Found JSON block but failed to parse")
        
        # Strategy 2: Look for any code blocks containing JSON
        code_blocks = re.finditer(r"```[\s\S]*?([\s\S]*?)```", text)
        for block in code_blocks:
            try:
                content = block.group(1).strip()
                if content.startswith('{') and content.endswith('}'):
                    json.loads(content)  # Validate JSON
                    return content
            except json.JSONDecodeError:
                continue
        
        # Strategy 3: Look for raw JSON objects in text using naive extraction
        i = 0
        length = len(text)
        
        while i < length:
            char = text[i]
            
            if char in ['{', '[']:
                start_char = char
                end_char = '}' if char == '{' else ']'
                
                nesting = 1
                j = i + 1
                
                # Track nesting levels until finding matching close bracket/brace
                while j < length and nesting > 0:
                    if text[j] == start_char:
                        nesting += 1
                    elif text[j] == end_char:
                        nesting -= 1
                    j += 1
                
                if nesting == 0:  # Found complete JSON structure
                    candidate = text[i:j]
                    try:
                        json.loads(candidate)  # Validate JSON
                        return candidate
                    except json.JSONDecodeError:
                        pass
                
                i = j  # Skip to end of current structure
            else:
                i += 1
        
        print("⚠️ No valid JSON found in response")
        return None
