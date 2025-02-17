from ceviche.core.workflow import Workflow
from ceviche.core.utilities.model_utils import ModelUtilsMixin
from ceviche.core.utilities.file_utils import WithReadAndWriteFilesMixin
from typing import Dict, Any

class EnhanceDraftWorkflow(
    Workflow,
    ModelUtilsMixin,
    WithReadAndWriteFilesMixin
):
    def __init__(self):
        super().__init__()

    def before_start(self, ctx: Dict[str, Any], args: Dict[str, Any]):
        super().before_start(ctx, args)
        print("EnhanceDraftWorkflow before_start")

        self.cleanup_task = self.load_task("cleanup", ctx, args)
        self.generate_logical_steps_task = self.load_task("generate_logical_steps", ctx, args)
        self.generate_step_proofs_task = self.load_task("generate_step_proofs", ctx, args)  # NEW TASK
        self.generate_examples_task = self.load_task("generate_examples", ctx, args)
        self.inject_images_task = self.load_task("inject_images", ctx, args)
        self.format_math_task = self.load_task("format_math", ctx, args)
        self.content_verification_task = self.load_task("content_verification", ctx, args)

    def run(self, ctx: Dict[str, Any], args: Dict[str, Any]) -> Any:
        print("EnhanceDraftWorkflow run")

        content = args.get("content")
        if not content:
            raise ValueError("Content is required in args for EnhanceDraftWorkflow.")
        base_directory = args.get("base_directory")
        directory = args.get("directory")

        # --- Iteration Loop ---
        for iteration in range(3):  # max_iterations=3
            print(f"Starting Enhancement Iteration {iteration + 1}")

            # --- Task Execution ---
            content = self.cleanup_task.run(ctx, {"content": content})
            content = self.generate_logical_steps_task.run(ctx, {"content": content})
            content = self.generate_step_proofs_task.run(ctx, {"content": content})
            content = self.generate_examples_task.run(ctx, {"content": content, "base_directory": base_directory})
            content = self.inject_images_task.run(ctx, {"content": content, "base_directory": base_directory})
            content = self.format_math_task.run(ctx, {"content": content})
            content = self.cleanup_task.run(ctx, {"content": content})

            # --- Verification ---
            verification_result = self.content_verification_task.run(ctx, {"content": content})
            if verification_result.strip().lower() == "yes":
                print("Content verification passed. Exiting enhancement loop.")
                break  # Exit loop if verification passes
            else:
                print("Content verification failed. Continuing to next iteration.")

        return content

    def after_start(self, ctx: Dict[str, Any], args: Dict[str, Any]):
        super().after_start(ctx, args)
        print("EnhanceDraftWorkflow after_start")
