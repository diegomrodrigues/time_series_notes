from ceviche.core.context import Context
from ceviche.core.task import Task
from typing import Any, Dict
from ceviche.core.utilities.model_utils import ModelUtilsMixin
from pathlib import Path
import re

class GenerateFilenameTask(Task, ModelUtilsMixin):
    def __init__(self, task_config: Dict[str, Any], task_name: str):
        super().__init__(task_config, task_name)

    def run(self, ctx: Context, args: Dict[str, Any]) -> str:
        """Generates a filename based on the provided topic."""

        self.model = self.init_model(ctx, args)

        topic = args.get("topic")
        if not topic:
            raise ValueError("A 'topic' argument must be provided.")

        prompt = self.prepare_prompt(self.task_config, content=topic)
        chat = self.start_chat()  # No files needed
        response = self.send_message(chat=chat, user_content=prompt)
        filename = response.text.strip()

        if ctx.get("mock_api"):
            return f"{topic}.md"

        #  Filename validation (from old FilenameHandler logic)
        if not filename:
            raise Exception("Filename generation failed to return a filename.")
        if not re.match(r"^[A-Za-z0-9 ]+$", filename):
            raise Exception(f"Invalid characters in filename: {filename}")
        if len(filename) > 50:
            raise Exception(f"Filename too long (max 50 chars): {filename}")
        if not filename[0].isalpha() or not filename[0].isupper():
            raise Exception(f"Filename must start with a capital letter: {filename}")
        if not all(word[0].isupper() or word.islower() for word in filename.split()):
            raise Exception(f"Filename must have proper spacing and capitalization: {filename}")

        return filename 