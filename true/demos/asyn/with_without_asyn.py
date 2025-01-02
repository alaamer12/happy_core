"""Example comparing code with and without Asyn."""

import asyncio
import logging
import random
from typing import List
from true.asyn import Asyn, TaskState

# === Parent-Child Example ===
async def child_task(name: str, delay: float = 0.5) -> str:
    """A simple child task."""
    await asyncio.sleep(delay)
    return f"Child {name} done"

async def without_asyn_parent_child():
    """Example of parent-child tasks without Asyn."""
    print("\nWithout Asyn:")
    
    # Create and run child tasks
    tasks = []
    for i in range(3):
        task = asyncio.create_task(child_task(f"task_{i}"))
        tasks.append(task)
    
    # Wait for all tasks
    try:
        results = await asyncio.gather(*tasks)
        print("Results:", results)
    except Exception as e:
        print(f"Error: {e}")
        # No automatic cleanup of child tasks
        for task in tasks:
            if not task.done():
                task.cancel()

async def with_asyn_parent_child():
    """Example of parent-child tasks with Asyn."""
    print("\nWith Asyn:")
    
    async with Asyn(name="parent") as parent:
        # Create child tasks
        child_tasks = []
        for i in range(3):
            task = await parent.create_task(
                child_task(f"task_{i}"),
                name=f"child_{i}"
            )
            child_tasks.append(task)
        
        # Run tasks with proper cleanup
        results = []
        for task in child_tasks:
            async with task:
                result = await task.run(child_task(task.info.name))
                results.append(result)
        
        print("Results:", results)

# === Resource Management Example ===
class Resource:
    """A simple resource that needs cleanup."""
    def __init__(self, name: str):
        self.name = name
        print(f"Created resource: {name}")
    
    async def cleanup(self):
        """Cleanup the resource."""
        await asyncio.sleep(0.1)  # Simulate cleanup work
        print(f"Cleaned up resource: {self.name}")

async def task_with_resource(name: str, resource: Resource) -> str:
    """A task that uses a resource."""
    await asyncio.sleep(random.uniform(0.1, 0.5))
    return f"Task {name} used {resource.name}"

async def without_asyn_resources():
    """Example of resource management without Asyn."""
    print("\nWithout Asyn:")
    
    # Create resources
    resources = [Resource(f"res_{i}") for i in range(2)]
    tasks = []
    
    try:
        # Create tasks using resources
        for i, resource in enumerate(resources):
            task = asyncio.create_task(task_with_resource(f"task_{i}", resource))
            tasks.append(task)
        
        # Wait for tasks
        results = await asyncio.gather(*tasks)
        print("Results:", results)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Manual cleanup
        for resource in resources:
            await resource.cleanup()

async def with_asyn_resources():
    """Example of resource management with Asyn."""
    print("\nWith Asyn:")
    
    async with Asyn(name="manager") as manager:
        # Create resources
        resources = [Resource(f"res_{i}") for i in range(2)]
        
        # Create tasks with resources
        task_results = []
        for i, resource in enumerate(resources):
            async with await manager.create_task(
                task_with_resource(f"task_{i}", resource),
                name=f"task_{i}"
            ) as task:
                result = await task.run(
                    task_with_resource(task.info.name, resource)
                )
                task_results.append(result)
        
        print("Results:", task_results)
        
        # Resources cleaned up automatically through task cleanup

async def main():
    """Run the examples."""
    print("=== Parent-Child Example ===")
    await without_asyn_parent_child()
    await with_asyn_parent_child()
    
    print("\n=== Resource Management Example ===")
    await without_asyn_resources()
    await with_asyn_resources()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
