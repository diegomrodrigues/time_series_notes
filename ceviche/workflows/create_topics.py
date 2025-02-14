from ceviche.core.context import Context
from ceviche.core.workflow import Workflow
from typing import Dict, Any
from ceviche.core.utilities.file_utils import WithReadAndWriteFilesMixin
from ceviche.core.utilities.json_utils import JsonUtilitiesMixin
import json

class CreateTopicsWorkflow(
    Workflow, 
    WithReadAndWriteFilesMixin, 
    JsonUtilitiesMixin
):

    def __init__(self):
        super().__init__()

    def before_start(self, ctx: Dict[str, Any], args: Dict[str, Any]):
        super().before_start(ctx, args)  # Call super to ensure hooks are called
        print("Starting CreateTopicsWorkflow")
        ctx["directory"] = args.get("directory", ".")

        self.create_topics = self.load_task("create_topics", ctx, args)
        self.consolidate_subtopics = self.load_task("consolidate_subtopics", ctx, args)

    def run(self, ctx: Dict[str, Any], args: Dict[str, Any]) -> Any:
        # --- Create Topics Task ---
        initial_topics = self.create_topics.run(ctx, args)
        ctx["initial_topics"] = initial_topics

        # --- Consolidate Subtopics Task ---
        consolidated_topics = self.consolidate_subtopics.run(ctx, args)
        ctx["consolidated_topics"] = consolidated_topics

        # --- Final Result Processing ---
        final_result_str = self.deduplicate_json_keys(
            json.dumps(consolidated_topics)
        )
        self.final_result = json.loads(final_result_str)

        ctx["topics"] = self.final_result

        return self.final_result

    def after_start(self, ctx: Dict[str, Any], args: Dict[str, Any]):
        super().after_start(ctx, args)  # Call super to ensure hooks are called
        json_str = self.dump_json(ctx["topics"])
        self.write_file(
            content=json_str,
            filename="topics.json"
        )
        print("CreateTopicsWorkflow completed")