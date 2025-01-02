"""Example of a task pipeline using Asyn."""

import asyncio
import logging
import sys
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from true.asyn import Asyn, TaskState, TaskPriority

# Create separate loggers for different types of output
diagnostic_logger = logging.getLogger('diagnostic')
progress_logger = logging.getLogger('progress')

@dataclass
class PipelineStage:
    """Represents a stage in the pipeline."""
    name: str
    process_time: float = 0.5
    fail_on_batch: Optional[str] = None  # Fail on specific batch
    retry_count: int = 2

@dataclass
class BatchResult:
    """Represents the result of batch processing."""
    batch_id: str
    stage_results: Dict[str, Any]
    success: bool
    error: Optional[str] = None

class Pipeline:
    """A pipeline for processing batches of data through multiple stages."""
    
    def __init__(self):
        self.stages = [
            PipelineStage("load", 0.2),
            PipelineStage("transform", 0.3),
            PipelineStage("validate", 0.1, "batch_1"),  # Fail on batch_1
            PipelineStage("save", 0.2)
        ]
        self._running = True
        self.results: Dict[str, BatchResult] = {}

    async def process_stage(self, batch_id: str, stage: PipelineStage, 
                          input_data: Any = None) -> Any:
        """Process a single stage for a batch."""
        for attempt in range(stage.retry_count + 1):
            try:
                # Simulate work
                await asyncio.sleep(stage.process_time)
                
                # Simulate controlled failure
                if stage.fail_on_batch == batch_id and attempt == 0:
                    raise Exception(f"Simulated failure in {stage.name}")
                
                # Simulate stage-specific processing
                if stage.name == "load":
                    result = f"Data loaded for batch {batch_id}"
                elif stage.name == "transform":
                    result = f"Transformed: {input_data}"
                elif stage.name == "validate":
                    result = f"Validated: {input_data}"
                else:  # save
                    result = f"Saved: {input_data}"
                
                if attempt > 0:
                    progress_logger.info(
                        f"Stage {stage.name} completed for batch {batch_id} "
                        f"after {attempt + 1} attempts"
                    )
                else:
                    progress_logger.info(
                        f"Stage {stage.name} completed for batch {batch_id}"
                    )
                return result
                
            except Exception as e:
                if attempt < stage.retry_count:
                    diagnostic_logger.warning(
                        f"Stage {stage.name} failed for batch {batch_id} "
                        f"(attempt {attempt + 1}/{stage.retry_count + 1}): {e}"
                    )
                    await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
                else:
                    raise Exception(
                        f"All {stage.retry_count + 1} attempts failed for {stage.name} "
                        f"on batch {batch_id}: {e}"
                    )

    async def process_batch(self, batch_id: str, pipeline_task: Asyn) -> BatchResult:
        """Process a batch through all pipeline stages."""
        stage_results = {}
        current_data = None
        
        try:
            for stage in self.stages:
                # Process stage with retries
                current_data = await self.process_stage(
                    batch_id, stage, current_data
                )
                stage_results[stage.name] = current_data
            
            return BatchResult(batch_id, stage_results, True)
            
        except Exception as e:
            diagnostic_logger.error(f"Error processing batch {batch_id}: {e}")
            return BatchResult(batch_id, stage_results, False, str(e))

    async def run(self, batch_ids: List[str]) -> Dict[str, BatchResult]:
        """Run the pipeline for multiple batches."""
        print("\n=== Pipeline Processing ===")
        
        async with Asyn(name="pipeline") as pipeline:
            # Process batches sequentially
            for batch_id in batch_ids:
                # Process batch
                result = await self.process_batch(batch_id, pipeline)
                self.results[batch_id] = result
            
            return self.results

async def main():
    """Run the pipeline example."""
    pipeline = Pipeline()
    batch_ids = [f"batch_{i}" for i in range(3)]
    
    try:
        results = await pipeline.run(batch_ids)
        
        # Print results
        print("\n=== Pipeline Results ===")
        for batch_id, result in results.items():
            print(f"\nBatch {batch_id}:")
            print(f"Success: {result.success}")
            if not result.success:
                print(f"Error: {result.error}")
            else:
                print("Stage Results:")
                for stage, output in result.stage_results.items():
                    print(f"  {stage}: {output}")
                    
    except Exception as e:
        diagnostic_logger.error(f"Pipeline error: {e}")

if __name__ == "__main__":
    # Configure diagnostic logging to stderr
    diagnostic_handler = logging.StreamHandler(sys.stderr)
    diagnostic_handler.setFormatter(logging.Formatter(
        '%(levelname)s:%(name)s: %(message)s'
    ))
    diagnostic_logger.addHandler(diagnostic_handler)
    diagnostic_logger.setLevel(logging.WARNING)  # Only show warnings and errors
    
    # Configure progress logging to stdout
    progress_handler = logging.StreamHandler(sys.stdout)
    progress_handler.setFormatter(logging.Formatter(
        '%(message)s'  # Simpler format for progress
    ))
    progress_logger.addHandler(progress_handler)
    progress_logger.setLevel(logging.INFO)
    
    # Run the pipeline
    asyncio.run(main())
