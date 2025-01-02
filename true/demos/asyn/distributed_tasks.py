"""Example of using Asyn for distributed task processing."""

import asyncio
import logging
import random
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from true.asyn import Asyn, TaskState, TaskPriority

# Create separate loggers
diagnostic_logger = logging.getLogger('diagnostic')
progress_logger = logging.getLogger('progress')

@dataclass
class Task:
    """Represents a task to be processed."""
    id: int
    data: str
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[int] = None
    retry_count: int = 0
    max_retries: int = 2

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class TaskResult:
    """Represents the result of a processed task."""
    task_id: int
    result: str
    success: bool
    error: Optional[str] = None

class Worker:
    """Simulates a worker that processes tasks."""
    
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.tasks_processed = 0
        self.tasks_failed = 0
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self._running = True

    async def process_task(self, task: Task) -> TaskResult:
        """Process a single task."""
        try:
            # Simulate work
            process_time = random.uniform(0.1, 0.5)
            await asyncio.sleep(process_time)
            
            # Simulate resource usage
            self.cpu_usage = random.uniform(0, 100)
            self.memory_usage = random.uniform(0, 1024)
            
            # Randomly fail some tasks
            if random.random() < 0.1 and task.retry_count < task.max_retries:  # 10% chance of failure
                raise Exception(f"Random failure for task {task.id}")
            
            result = f"Task {task.id} processed by Worker {self.worker_id}"
            self.tasks_processed += 1
            
            progress_logger.info(
                f"Worker {self.worker_id} completed task {task.id} "
                f"(processed: {self.tasks_processed}, failed: {self.tasks_failed})"
            )
            return TaskResult(task.id, result, True)
            
        except Exception as e:
            self.tasks_failed += 1
            diagnostic_logger.error(
                f"Worker {self.worker_id} failed task {task.id}: {e} "
                f"(processed: {self.tasks_processed}, failed: {self.tasks_failed})"
            )
            return TaskResult(task.id, "", False, str(e))

    def get_stats(self) -> Dict:
        """Get worker statistics."""
        return {
            "tasks_processed": self.tasks_processed,
            "tasks_failed": self.tasks_failed,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage
        }

class DistributedTaskManager:
    """Manages distributed task processing using Asyn."""
    
    def __init__(self, num_workers: int = 2):
        self.workers = [Worker(i) for i in range(num_workers)]
        self.task_queue: asyncio.Queue[Task] = asyncio.Queue()
        self.result_queue: asyncio.Queue[TaskResult] = asyncio.Queue()
        self.tasks: Dict[int, Task] = {}
        self.results: Dict[int, TaskResult] = {}
        self.pending_tasks: Set[int] = set()
        self._running = True

    async def submit_task(self, task: Task):
        """Submit a task for processing."""
        self.tasks[task.id] = task
        self.pending_tasks.add(task.id)
        await self.task_queue.put(task)
        progress_logger.info(f"Submitted task {task.id} (dependencies: {task.dependencies})")

    async def process_results(self) -> None:
        """Process completed task results."""
        try:
            while self._running:
                result = await self.result_queue.get()
                task = self.tasks[result.task_id]
                
                if not result.success and task.retry_count < task.max_retries:
                    # Retry failed task
                    task.retry_count += 1
                    diagnostic_logger.warning(
                        f"Retrying task {task.id} (attempt {task.retry_count + 1})"
                    )
                    await self.task_queue.put(task)
                else:
                    # Store final result
                    self.results[result.task_id] = result
                    self.pending_tasks.remove(result.task_id)
                    
                    if not result.success:
                        diagnostic_logger.error(
                            f"Task {result.task_id} failed after {task.retry_count + 1} attempts: "
                            f"{result.error}"
                        )
                    else:
                        progress_logger.info(
                            f"Task {result.task_id} completed: {result.result}"
                        )
                
                self.result_queue.task_done()
                
                # Check if all tasks are done
                if not self.pending_tasks:
                    self._running = False
                
        except asyncio.CancelledError:
            progress_logger.info("Result processor cancelled")
            raise
        except Exception as e:
            diagnostic_logger.error(f"Error in result processor: {e}")
            raise

    async def worker_loop(self, worker: Worker) -> None:
        """Main worker loop."""
        try:
            while self._running:
                try:
                    task = await self.task_queue.get()
                    
                    # Check dependencies
                    dependencies_met = all(
                        dep_id in self.results and self.results[dep_id].success
                        for dep_id in task.dependencies
                    )
                    
                    if not dependencies_met:
                        # Put task back in queue
                        await self.task_queue.put(task)
                        await asyncio.sleep(0.1)
                        continue
                    
                    result = await worker.process_task(task)
                    await self.result_queue.put(result)
                    self.task_queue.task_done()
                    
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    diagnostic_logger.error(f"Error in worker {worker.worker_id}: {e}")
                    
        except asyncio.CancelledError:
            progress_logger.info(f"Worker {worker.worker_id} cancelled")
            raise

    async def monitor_workers(self) -> None:
        """Monitor worker statistics."""
        try:
            while self._running:
                stats = []
                for worker in self.workers:
                    worker_stats = worker.get_stats()
                    stats.append(
                        f"Worker {worker.worker_id}:\n"
                        f"  Tasks Processed: {worker_stats['tasks_processed']}\n"
                        f"  Tasks Failed: {worker_stats['tasks_failed']}\n"
                        f"  CPU Usage: {worker_stats['cpu_usage']:.1f}%\n"
                        f"  Memory Usage: {worker_stats['memory_usage']:.1f} MB"
                    )
                
                print("\n=== Worker Statistics ===\n")
                print("\n".join(stats))
                print(f"\nPending Tasks: {len(self.pending_tasks)}")
                print("="*24 + "\n")
                
                await asyncio.sleep(2)
                
        except asyncio.CancelledError:
            progress_logger.info("Worker monitor cancelled")
            raise
        except Exception as e:
            diagnostic_logger.error(f"Error in worker monitor: {e}")
            raise

    async def start(self):
        """Start the distributed task manager."""
        print("\n=== Starting Distributed Task Manager ===\n")
        
        try:
            async with Asyn(name="task_manager") as manager:
                # Start result processor
                result_processor = await manager.create_task(
                    self.process_results(),
                    name="result_processor"
                )
                
                # Start worker monitor
                monitor = await manager.create_task(
                    self.monitor_workers(),
                    name="worker_monitor"
                )
                
                # Start workers
                worker_tasks = []
                for worker in self.workers:
                    task = await manager.create_task(
                        self.worker_loop(worker),
                        name=f"worker_{worker.worker_id}"
                    )
                    worker_tasks.append(task)
                
                # Submit some test tasks
                for i in range(5):  # Reduced to 5 tasks
                    task = Task(
                        id=i,
                        data=f"Test data {i}",
                        priority=random.choice(list(TaskPriority)),
                        dependencies=[j for j in range(i) if random.random() < 0.3]
                    )
                    await self.submit_task(task)
                
                # Wait for tasks to complete
                while self._running:
                    await asyncio.sleep(0.1)
                
                # Print final results
                print("\n=== Final Results ===\n")
                for task_id, result in sorted(self.results.items()):
                    print(f"Task {task_id}:")
                    print(f"  Success: {result.success}")
                    if result.success:
                        print(f"  Result: {result.result}")
                    else:
                        print(f"  Error: {result.error}")
                    print()
                
        finally:
            # Stop all tasks
            self._running = False

async def main():
    """Run the distributed task example."""
    manager = DistributedTaskManager(num_workers=2)  # Back to 2 workers
    await manager.start()

if __name__ == "__main__":
    # Configure diagnostic logging to stderr
    diagnostic_handler = logging.StreamHandler(sys.stderr)
    diagnostic_handler.setFormatter(logging.Formatter(
        '%(levelname)s:%(name)s: %(message)s'
    ))
    diagnostic_logger.addHandler(diagnostic_handler)
    diagnostic_logger.setLevel(logging.WARNING)
    
    # Configure progress logging to stdout
    progress_handler = logging.StreamHandler(sys.stdout)
    progress_handler.setFormatter(logging.Formatter(
        '%(message)s'  # Simpler format for progress
    ))
    progress_logger.addHandler(progress_handler)
    progress_logger.setLevel(logging.INFO)
    
    # Run the distributed task manager
    asyncio.run(main())
