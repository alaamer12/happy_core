"""Advanced usage examples of the Asyn class."""

import asyncio
import psutil
from true.asyn import Asyn, TaskPriority, TaskState

async def simple_task():
    """A simple async task that sleeps."""
    await asyncio.sleep(0.1)
    return "Done!"

async def cpu_intensive():
    """Simulate CPU-intensive task."""
    result = 0
    for i in range(1000000):
        result += i
    return result

async def memory_intensive():
    """Simulate memory-intensive task."""
    big_list = [i for i in range(1000000)]
    await asyncio.sleep(0.1)
    return len(big_list)

async def priority_example():
    """Example of task priorities."""
    async with Asyn(name="main") as main:
        # Create tasks with different priorities
        async with Asyn(name="high_priority", parent=main, priority=TaskPriority.HIGH) as high_task:
            async with Asyn(name="low_priority", parent=main, priority=TaskPriority.LOW) as low_task:
                # Run tasks
                results = await asyncio.gather(
                    high_task.run(cpu_intensive()),
                    low_task.run(cpu_intensive())
                )
                print(f"Tasks completed with results: {results}")

async def resource_limits_example():
    """Example of resource limits."""
    async with Asyn(name="main") as main:
        # Set resource limits
        main.info.limits.max_memory = 1024*1024*10  # 10MB
        main.info.limits.max_runtime = 5  # 5 seconds
        main.info.limits.max_children = 2  # max 2 child tasks
        
        try:
            # Try to exceed memory limit
            await main.run(memory_intensive())
        except Exception as e:
            print(f"Task failed due to resource limits: {e}")

async def dependency_example():
    """Example of task dependencies."""
    async with Asyn(name="main") as main:
        async with Asyn(name="task1", parent=main) as task1:
            async with Asyn(name="task2", parent=main) as task2:
                async with Asyn(name="task3", parent=main) as task3:
                    # Set up dependencies: task2 depends on task1, task3 depends on task2
                    task2.info.add_dependency(task1)
                    task3.info.add_dependency(task2)
                    
                    # This will run in the correct order due to dependencies
                    results = await asyncio.gather(
                        task3.run(simple_task()),
                        task2.run(simple_task()),
                        task1.run(simple_task())
                    )
                    print(f"Dependent tasks completed in order with results: {results}")

async def monitoring_example():
    """Example of task monitoring and statistics."""
    async with Asyn(name="monitored") as task:
        start_time = asyncio.get_event_loop().time()
        
        # Run a task while monitoring its resources
        await task.run(cpu_intensive())
        
        end_time = asyncio.get_event_loop().time()
        
        # Get task statistics
        stats = task.info.stats
        stats.total_runtime = end_time - start_time
        
        print(f"Task Statistics:")
        print(f"Peak Memory: {stats.peak_memory / 1024 / 1024:.2f} MB")
        print(f"Runtime: {stats.total_runtime:.2f} seconds")
        print(f"Child Tasks: {stats.child_tasks}")
        print(f"Final State: {task.info.state}")

async def main():
    """Run all examples."""
    print("=== Priority Example ===")
    await priority_example()
    
    print("\n=== Resource Limits Example ===")
    await resource_limits_example()
    
    print("\n=== Dependency Example ===")
    await dependency_example()
    
    print("\n=== Monitoring Example ===")
    await monitoring_example()

if __name__ == "__main__":
    asyncio.run(main())
