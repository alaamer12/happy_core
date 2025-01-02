"""Basic usage examples of the Asyn class."""

import asyncio
from true.asyn import Asyn

async def simple_task():
    """A simple async task that sleeps."""
    await asyncio.sleep(1)
    return "Done!"

async def basic_example():
    """Basic example of creating and running a task."""
    async with Asyn(name="main") as main:
        result = await main.run(simple_task())
        print(f"Task completed with result: {result}")

async def parent_child_example():
    """Example of parent-child task relationships."""
    async with Asyn(name="parent") as parent:
        # Create child tasks
        async with Asyn(name="child1", parent=parent) as child1:
            async with Asyn(name="child2", parent=parent) as child2:
                # Run children
                results = await asyncio.gather(
                    child1.run(simple_task()),
                    child2.run(simple_task())
                )
                print(f"Children completed with results: {results}")

async def cancellation_example():
    """Example of task cancellation."""
    async def long_task():
        try:
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            print("Task was cancelled!")
            raise
    
    async with Asyn(name="main") as main:
        # Start the task
        async with await main.create_task(long_task()) as task:
            # Wait a bit then cancel
            await asyncio.sleep(0.5)
            await main.cancel(reason="Demo cancellation")

async def main():
    """Run all examples."""
    print("=== Basic Example ===")
    await basic_example()
    
    print("\n=== Parent-Child Example ===")
    await parent_child_example()
    
    print("\n=== Cancellation Example ===")
    await cancellation_example()

if __name__ == "__main__":
    asyncio.run(main())
