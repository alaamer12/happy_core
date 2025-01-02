"""Examples of using Asyn with asyncio compatibility features."""

import asyncio
from typing import List
from true.asyn import Asyn, TaskState

async def simple_task(delay: float = 0.1):
    """A simple async task that sleeps."""
    await asyncio.sleep(delay)
    return "Done!"

async def gather_example():
    """Example of using asyncio.gather with Asyn tasks."""
    print("\n=== Gather Example ===")
    async with Asyn(name="parent") as parent:
        # Create multiple child tasks
        children = []
        for i in range(3):
            async with await parent.create_task(simple_task(0.1 * (i + 1))) as child:
                children.append(child)
        
        # Gather results
        results = await asyncio.gather(
            *[child.run(simple_task()) for child in children]
        )
        print(f"Gather results: {results}")

async def wait_example():
    """Example of using asyncio.wait with Asyn tasks."""
    print("\n=== Wait Example ===")
    async with Asyn(name="parent") as parent:
        # Create tasks with different delays
        tasks = []
        for i in range(3):
            async with await parent.create_task(simple_task(0.1 * (i + 1))) as child:
                task = asyncio.create_task(child.run(simple_task()))
                tasks.append(task)
        
        # Wait for tasks with timeout
        done, pending = await asyncio.wait(
            tasks,
            timeout=0.2,
            return_when=asyncio.FIRST_COMPLETED
        )
        
        print(f"Completed tasks: {len(done)}")
        print(f"Pending tasks: {len(pending)}")
        
        # Clean up pending tasks
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.wait(pending)

async def shield_example():
    """Example of using asyncio.shield with Asyn tasks."""
    print("\n=== Shield Example ===")
    async with Asyn(name="parent") as parent:
        async with await parent.create_task(simple_task(0.5)) as protected_task:
            # Shield the task from cancellation
            shielded = asyncio.shield(protected_task.run(simple_task()))
            
            try:
                # Try to cancel the parent task
                task = asyncio.create_task(
                    asyncio.sleep(0.1)
                )
                await asyncio.gather(
                    shielded,
                    task
                )
            except asyncio.CancelledError:
                print("Parent was cancelled but shielded task continues")
                # Wait for shielded task to complete
                await shielded
                print("Shielded task completed")

async def as_completed_example():
    """Example of using asyncio.as_completed with Asyn tasks."""
    print("\n=== As Completed Example ===")
    async with Asyn(name="parent") as parent:
        # Create tasks with different delays
        tasks = []
        for i in range(3):
            async with await parent.create_task(simple_task(0.3 - 0.1 * i)) as child:
                task = asyncio.create_task(child.run(simple_task()))
                tasks.append(task)
        
        # Process tasks as they complete
        for i, future in enumerate(asyncio.as_completed(tasks)):
            result = await future
            print(f"Task {i} completed with result: {result}")

async def main():
    """Run all examples."""
    await gather_example()
    await wait_example()
    await shield_example()
    await as_completed_example()

if __name__ == "__main__":
    asyncio.run(main())
