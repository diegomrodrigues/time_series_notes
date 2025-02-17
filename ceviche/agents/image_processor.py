from pathlib import Path
from typing import Dict, Any
from ceviche.core.agent import Agent
from ceviche.core.context import Context

class ImageProcessorAgent(Agent):
    """Processes images within directory structures and generates metadata."""
    
    def __init__(self, debug: bool = False):
        super().__init__(debug)
        self.debug = debug

    def pre_execution(self, ctx: Context, args: Dict[str, Any]):
        """Prepare context for image processing."""
        if self.debug:
            print("ImageProcessor: pre_execution")
        ctx["base_dir"] = args.get("directory", ".")
        ctx["excluded_dirs"] = args.get("excluded_folders", [])
        ctx["debug"] = self.debug

    def execute(self, ctx: Context, args: Dict[str, Any]) -> Any:
        """Main execution method for image processing."""
        base_dir = Path(ctx["base_dir"])
        excluded_dirs = ctx["excluded_dirs"]
        
        try:
            if self.debug:
                print(f"Starting image processing in: {base_dir}")
            
            # Get the process_images workflow
            process_images_workflow = self.get_workflow("process_images", ctx, args)
            
            # Run the workflow with directory context
            workflow_args = {
                "base_dir": str(base_dir),
                "excluded_dirs": excluded_dirs,
                "pdf_file": self._find_pdf_file(base_dir)
            }
            
            process_images_workflow.run(ctx, workflow_args)
            
            if self.debug:
                print("Image processing completed successfully")
                
        except Exception as e:
            print(f"❌ Image processing failed: {str(e)}")
            raise

    def _find_pdf_file(self, directory: Path) -> str:
        """Find first PDF file in directory for context."""
        pdf_files = list(directory.glob("*.pdf"))
        if pdf_files:
            return str(pdf_files[0])
        return ""

    def post_execution(self, ctx: Context, args: Dict[str, Any], result: Any):
        """Cleanup after processing."""
        if self.debug:
            print("ImageProcessor: post_execution") 