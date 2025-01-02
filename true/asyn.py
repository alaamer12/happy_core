"""
Advanced Asynchronous Task Management System.

This module provides a comprehensive task management system built on top of asyncio,
offering structured parent-child relationships, enhanced lifecycle management,
and improved debugging capabilities.
"""

import asyncio
import logging
import inspect
import weakref
import traceback
import sys
from typing import Optional, Dict, Set, List, Any, Callable, Coroutine, Union, AsyncIterator, TypeVar, Tuple
from enum import Enum
from contextlib import contextmanager, AsyncExitStack
import time
import psutil
import functools

T = TypeVar('T')

ServerType = Coroutine[Any, Any, asyncio.Server]

def requires_py311(fallback: Optional[Callable] = None):
    """Decorator to handle Python 3.11+ specific features with fallback."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if sys.version_info >= (3, 11):
                return await func(*args, **kwargs)
            elif fallback:
                return await fallback(*args, **kwargs)
            else:
                raise RuntimeError(f"{func.__name__} requires Python 3.11 or higher")
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if sys.version_info >= (3, 11):
                return func(*args, **kwargs)
            elif fallback:
                return fallback(*args, **kwargs)
            else:
                raise RuntimeError(f"{func.__name__} requires Python 3.11 or higher")
        
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
    return decorator

class TaskState(Enum):
    """Enum representing possible states of an async task."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"  # New state for deadlock detection

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class ResourceStats:
    """Track resource usage statistics."""
    def __init__(self):
        self.peak_memory: int = 0
        self.total_runtime: float = 0
        self.io_operations: int = 0
        self.network_calls: int = 0
        self.child_tasks: int = 0

class ResourceLimits:
    """Define resource usage limits."""
    def __init__(self):
        self.max_memory: Optional[int] = None
        self.max_runtime: Optional[float] = None
        self.max_io_ops: Optional[int] = None
        self.max_network_calls: Optional[int] = None
        self.max_children: Optional[int] = None

class TaskInfo:
    """Container for task metadata and state information."""
    def __init__(self, name: str, parent: Optional['Asyn'] = None):
        self.name = name
        self.state = TaskState.PENDING
        self.priority = TaskPriority.NORMAL
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.exception: Optional[Exception] = None
        self._parent = weakref.proxy(parent) if parent else None
        self.children = weakref.WeakSet()
        self.task: Optional[asyncio.Task] = None
        self.debug_info: Dict[str, Any] = {}
        self._cleanup_handlers: List[Callable] = []
        self.done_callback_added = False
        self._zombie_check_handle: Optional[asyncio.Handle] = None
        self.resources: Set[Any] = set()
        self.dependencies = weakref.WeakSet()
        self.dependents = weakref.WeakSet()
        self.stats = ResourceStats()
        self.limits = ResourceLimits()
        self._blocked_by = weakref.WeakSet()
        self._last_active: float = 0
        self._starvation_threshold: float = 60  # seconds


    def add_dependency(self, task: 'Asyn') -> None:
        """Add a task dependency."""
        self.dependencies.add(task)
        task.info.dependents.add(self)

    def remove_dependency(self, task: 'Asyn') -> None:
        """Remove a task dependency."""
        self.dependencies.discard(task)
        task.info.dependents.discard(self)

    # noinspection PyTypeChecker
    def check_deadlock(self) -> Optional[Set['Asyn']]:
        """Check for deadlock in task dependencies."""
        visited = set()
        path = []

        # noinspection PyCompatibility
        def visit(task: 'Asyn'):
            if task in path:
                return set(path[path.index(task):])
            if task in visited:
                return None
                
            visited.add(task)
            path.append(task)
            
            for dep in task.info.dependencies:
                if cycle := visit(dep):
                    return cycle
                    
            path.pop()
            return None
            
        return visit(self)

    def update_stats(self) -> None:
        """Update resource usage statistics."""
        if self.task:
            try:
                process = psutil.Process()
                self.stats.peak_memory = max(self.stats.peak_memory, process.memory_info().rss)
            except ImportError:
                pass
            
        if self.start_time:
            self.stats.total_runtime = time.time() - self.start_time
            
        self.stats.child_tasks = len(self.children)

    def check_resource_limits(self) -> Optional[str]:
        """Check if any resource limits are exceeded."""
        if self.limits.max_memory and self.stats.peak_memory > self.limits.max_memory:
            return f"Memory limit exceeded: {self.stats.peak_memory} > {self.limits.max_memory}"
            
        if self.limits.max_runtime and self.stats.total_runtime > self.limits.max_runtime:
            return f"Runtime limit exceeded: {self.stats.total_runtime} > {self.limits.max_runtime}"
            
        if self.limits.max_children and len(self.children) > self.limits.max_children:
            return f"Child task limit exceeded: {len(self.children)} > {self.limits.max_children}"
            
        return None

    def check_starvation(self, current_time: float) -> bool:
        """Check if task is potentially starving."""
        return (self.state == TaskState.BLOCKED and 
                current_time - self._last_active > self._starvation_threshold)


# noinspection PyProtectedMember
class AsynCleanup:
    """Handles cleanup of Asyn tasks and resources."""
    
    def __init__(self, task: 'Asyn'):
        self._task = task
        self._cleaned = False

    async def __aenter__(self):
        """No setup needed."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Perform cleanup on exit."""
        if self._cleaned:
            return
        
        try:
            # Cancel monitor task first
            if self._task._monitor_task and not self._task._monitor_task.done():
                self._task._monitor_task.cancel()
                try:
                    await self._task._monitor_task
                except (asyncio.CancelledError, Exception):
                    pass

            # Cancel all children first
            await self._cancel_children()

            # Cancel self if still active
            if self._task._info.task and not self._task._info.task.done():
                await self._cancel_self()

            # Run cleanup callbacks and cleanup resources
            await self._run_cleanup_callbacks()
            await self._cleanup_resources()

            # Update final state
            self._update_final_state(exc_type, exc_val)
            
            self._cleaned = True

        except Exception as e:
            logging.error(f"Error during cleanup for {self._task.name}: {str(e)}")
            raise

    async def _cancel_children(self, timeout: float = 1.0):
        """Cancel all child tasks."""
        cancel_tasks = []
        for child in list(self._task.info.children):
            try:
                task = asyncio.create_task(
                    child._cancel_self(reason=f"Parent {self._task.name} cleanup")
                )
                cancel_tasks.append(task)
            except ReferenceError:
                continue

        if cancel_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*cancel_tasks, return_exceptions=True),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logging.warning(
                    f"Timeout waiting for children of {self._task.name} to cancel"
                )

    async def _cancel_self(self, reason: str = "Cleanup"):
        """Cancel the task itself."""
        if self._task.info.task and not self._task.info.task.done():
            self._task.info.state = TaskState.CANCELLED
            self._task.info.debug_info['cancel_reason'] = reason
            self._task.info.task.cancel()
            try:
                await self._task.info.task
            except (asyncio.CancelledError, Exception):
                pass

    async def _run_cleanup_callbacks(self):
        """Run registered cleanup callbacks."""
        for callback in self._task._cleanup_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logging.error(f"Error in cleanup callback: {str(e)}")

    async def _cleanup_resources(self):
        """Clean up task resources."""
        if self._task.info:
            self._task.info.end_time = self._task._loop.time()
            self._task.info.update_stats()
            
            # Remove from parent's children set
            if self._task.info._parent:
                try:
                    self._task.info._parent.info.children.discard(self._task)
                except (ReferenceError, AttributeError):
                    pass

    def _update_final_state(self, exc_type, exc_val):
        """Update the final state of the task based on exit condition."""
        if exc_type is None:
            self._task.info.state = TaskState.COMPLETED
        elif exc_type is asyncio.CancelledError:
            self._task.info.state = TaskState.CANCELLED
        else:
            self._task.info.state = TaskState.FAILED
            self._task.info.exception = exc_val

class Asyn:
    """
    Advanced asynchronous task management system with structured parent-child relationships.
    Fully compatible with Python 3.11+ features including TaskGroup.
    """
    
    ZOMBIE_CHECK_INTERVAL = 60  # seconds
    MAX_ZOMBIE_AGE = 300  # seconds
    
    def __init__(self, name: str = None, parent: Optional['Asyn'] = None,
                 loop: Optional[asyncio.AbstractEventLoop] = None,
                 debug: bool = None,
                 priority: TaskPriority = TaskPriority.NORMAL):
        self.name = name or f"Task-{id(self)}"
        self._info = TaskInfo(self.name, parent)
        self._info.priority = priority
        self._loop = loop or asyncio.get_event_loop()
        self._cleanup_callbacks: List[Callable] = []
        self._monitor_task: Optional[asyncio.Task] = None
        
        if debug is not None:
            self._loop.set_debug(debug)
        
        if parent:
            parent._info.children.add(self)
            
        self._start_monitoring()

    @property
    def info(self):
        return self._info

    def _start_monitoring(self) -> None:
        """Start monitoring this task and its children."""
        if not self._monitor_task:
            self._monitor_task = self._loop.create_task(self._monitor())
            self._monitor_task.add_done_callback(self._monitor_done_callback)

    def _monitor_done_callback(self, task: asyncio.Task) -> None:
        """Handle completion of the monitor task."""
        try:
            task.result()  # This will raise any exception that occurred
        except asyncio.CancelledError:
            pass  # Normal cancellation
        except Exception as e:
            logging.error(f"Monitor task for {self.name} failed: {e}")
        finally:
            self._monitor_task = None  # Clear the reference

    # noinspection PyCompatibility
    async def _monitor(self) -> None:
        """Monitor task and children for zombies, deadlocks, and resource limits."""
        try:
            # Check task state
            if self._info:
                self._check_task_state()
                await self._check_children()
                await self._cleanup_zombies()
        except Exception as e:
            logging.error(f"Error in task monitor for {self.name}: {str(e)}")

    def _check_task_state(self) -> None:
        """Check task state and update if necessary."""
        if self._info.state == TaskState.RUNNING:
            self._info._last_active = self._loop.time()

    async def _check_children(self) -> None:
        """Check children's state and clean up if necessary."""
        for child in list(self.info.children):
            try:
                if child.info.state in (TaskState.COMPLETED, TaskState.CANCELLED, TaskState.FAILED):
                    await self._cleanup_child(child)
            except Exception as e:
                logging.error(f"Error checking child {child.name}: {str(e)}")

    async def _cleanup_child(self, child: 'Asyn') -> None:
        """Clean up a child task."""
        try:
            await child.cleanup().__aexit__(None, None, None)
            self.info.children.discard(child)
        except Exception as e:
            logging.error(f"Error cleaning up child {child.name}: {str(e)}")

    async def _cleanup_zombies(self) -> None:
        """Clean up zombie tasks."""
        current_time = self._loop.time()
        for child in list(self.info.children):
            try:
                if (child.info.state != TaskState.RUNNING and 
                    child.info.task and 
                    child.info.task.done() and
                    not child.info.task.cancelled()):
                    # Task is done but hasn't been cleaned up
                    if not child.info.end_time:
                        child.info.end_time = current_time
                    elif current_time - child.info.end_time > self.MAX_ZOMBIE_AGE:
                        await self._cleanup_child(child)
            except ReferenceError:
                continue

    def set_priority(self, priority: TaskPriority) -> None:
        """Set task priority level."""
        self._info.priority = priority

    def add_dependency(self, task: 'Asyn') -> None:
        """Add a task that must complete before this one."""
        self._info.add_dependency(task)

    def remove_dependency(self, task: 'Asyn') -> None:
        """Remove a task dependency."""
        self._info.remove_dependency(task)

    async def wait_dependencies(self) -> None:
        """Wait for all dependencies to complete."""
        if self._info.dependencies:
            deps = [dep.info.task for dep in self._info.dependencies if dep.info.task]
            await asyncio.gather(*deps)

    def set_resource_limit(self, **limits) -> None:
        """Set resource usage limits."""
        for name, value in limits.items():
            setattr(self._info.limits, f"max_{name}", value)

    async def run(self, coroutine: Coroutine) -> Any:
        """Run a coroutine as a managed task with full lifecycle tracking."""
        self._info.state = TaskState.RUNNING
        self._info.start_time = self._loop.time()
        
        try:
            return await coroutine
        except asyncio.CancelledError:
            self._info.state = TaskState.CANCELLED
            raise
        except Exception as e:
            self._info.state = TaskState.FAILED
            self._info.exception = e
            raise
        finally:
            self._info.state = TaskState.COMPLETED
            self._info.end_time = self._loop.time()
            await self.cleanup().__aexit__(None, None, None)

    def _task_done_callback(self, task: asyncio.Task) -> None:
        """Handle task completion."""
        try:
            exc = task.exception()
            if exc:
                self._info.state = TaskState.FAILED
                self._info.exception = exc
            elif task.cancelled():
                self._info.state = TaskState.CANCELLED
            else:
                self._info.state = TaskState.COMPLETED
        except asyncio.CancelledError:
            self._info.state = TaskState.CANCELLED
        except Exception as e:
            self._info.state = TaskState.FAILED
            self._info.exception = e
        
        self._info.end_time = self._loop.time()

    async def _cancel_self(self, reason: Optional[str] = None) -> None:
        """Cancel this task only."""
        if self._info.task and not self._info.task.done():
            self._info.state = TaskState.CANCELLED
            self._info.debug_info['cancel_reason'] = reason
            self._info.task.cancel()
            try:
                await self._info.task
            except (asyncio.CancelledError, Exception):
                pass

    # noinspection PyProtectedMember
    async def _cancel_children(self, timeout: Optional[float] = None, reason: Optional[str] = None) -> None:
        """Cancel all children with timeout."""
        cancel_tasks = []
        for child in list(self.info.children):
            try:
                # Create a task for each child's cancellation
                task = asyncio.create_task(child._cancel_self(reason=f"Parent cancelled: {reason}"))
                cancel_tasks.append(task)
            except ReferenceError:
                continue

        if cancel_tasks:
            try:
                # Wait for all cancellations with timeout
                if timeout is not None:
                    await asyncio.wait_for(
                        asyncio.gather(*cancel_tasks, return_exceptions=True),
                        timeout=timeout
                    )
                else:
                    await asyncio.gather(*cancel_tasks, return_exceptions=True)
            except asyncio.TimeoutError:
                logging.warning(f"Timeout waiting for children of {self.name} to cancel")

    async def _cancel_with_timeout(self, timeout: Optional[float]) -> None:
        """Cancel this task and all children with timeout."""
        if timeout:
            try:
                await asyncio.wait_for(self._info.task, timeout=timeout)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass
    
    async def _notify_dependents(self, reason: Optional[str] = None) -> None:
        """Notify all dependents that this task was cancelled."""
        for dependent in list(self._info.dependents):
            try:
                dependent.info.state = TaskState.BLOCKED
                dependent.info.debug_info['blocked_reason'] = f"Dependency cancelled: {self.name} ({reason})"
            except ReferenceError:
                continue
    
    async def cancel(self, include_children: bool = True, timeout: Optional[float] = None, reason: Optional[str] = None) -> None:
        """Cancel this task and optionally all its children with timeout."""
        await self._cancel_self(reason)
        if include_children:
            await self._cancel_children(timeout, reason)
        await self._cancel_with_timeout(timeout)
        await self._notify_dependents(reason)
        await self.cleanup().__aexit__(None, None, None)

    def cleanup(self) -> AsynCleanup:
        """Get a cleanup context manager for this task."""
        return AsynCleanup(self)

    async def __aenter__(self):
        """Async context manager support."""
        if self._info.state == TaskState.PENDING:
            self._info.state = TaskState.RUNNING
            self._info.start_time = self._loop.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on async context manager exit."""
        async with self.cleanup():
            pass

    def __del__(self):
        """Ensure resources are cleaned up on deletion."""
        if self._info and self._info.state not in (TaskState.COMPLETED, TaskState.CANCELLED, TaskState.FAILED):
            logging.warning(f"Task {self.name} was garbage collected while still active")
            if self._loop and self._loop.is_running():
                self._loop.create_task(self.cancel())

    @property
    def state(self) -> TaskState:
        """Current state of the task."""
        return self._info.state
    
    @property
    def children(self):
        """Set of child tasks."""
        return self._info.children
    
    @property
    def parent(self) -> Optional['Asyn']:
        """Parent task if exists."""
        return self.parent

    async def create_task(self, coro: Coroutine, *, name: Optional[str] = None) -> 'Asyn':
        """Create a new child task."""
        child = Asyn(name=name or f"child-{len(self.info.children)}", parent=self)
        child._info.task = self._loop.create_task(coro)
        child._info.task.add_done_callback(child._task_done_callback)
        return child

    def create_future(self) -> asyncio.Future:
        """Create a new future in the task's event loop."""
        return self._loop.create_future()

    async def run_in_executor(self, executor: Optional[Any], func: Callable, *args) -> Any:
        """Run a function in an executor."""
        return await self._loop.run_in_executor(executor, func, *args)

    def call_soon(self, callback: Callable, *args) -> asyncio.Handle:
        """Schedule a callback to run soon."""
        return self._loop.call_soon(callback, *args)

    def call_later(self, delay: float, callback: Callable, *args) -> asyncio.Handle:
        """Schedule a callback to run after a delay."""
        return self._loop.call_later(delay, callback, *args)

    def call_at(self, when: float, callback: Callable, *args) -> asyncio.Handle:
        """Schedule a callback to run at a specific time."""
        return self._loop.call_at(when, callback, *args)


    @classmethod
    def create_task_group(cls, parent: Optional['Asyn'] = None) -> 'AsyncTaskGroup':
        """Create a new task group for concurrent task execution."""
        return AsyncTaskGroup(parent)

    @classmethod
    def get_current_task(cls, loop: Optional[asyncio.AbstractEventLoop] = None) -> Optional['Asyn']:
        """Get the current task wrapper."""
        loop = loop or asyncio.get_event_loop()
        task = asyncio.current_task(loop)
        return cls(name=task.get_name()) if task else None

    @classmethod
    def all_tasks(cls, loop: Optional[asyncio.AbstractEventLoop] = None) -> Set['Asyn']:
        """Get all tasks in the loop."""
        loop = loop or asyncio.get_event_loop()
        return {cls(name=task.get_name()) for task in asyncio.all_tasks(loop)}

    async def ensure_future(self, coro_or_future: Union[Coroutine, asyncio.Future], *, name: Optional[str] = None) -> Any:
        """Wrap ensure_future with task management."""
        task = asyncio.ensure_future(coro_or_future, loop=self._loop)
        child = self.__class__(name=name or f"future-{len(self.children)}", parent=self)
        child._info.task = task
        return await task

    def create_server(self, client_connected_cb: Callable, host: str = None, port: int = None, **kwargs) -> ServerType:
        """Create a TCP server."""
        return self._loop.create_server(client_connected_cb, host, port, **kwargs)

    def create_unix_server(self, client_connected_cb: Callable, path: str = None, **kwargs) -> ServerType:
        """Create a Unix domain socket server."""
        return self._loop.create_unix_server(client_connected_cb, path, **kwargs)

    def create_connection(self, protocol_factory: Callable, host: str = None, port: int = None, **kwargs) -> Coroutine:
        """Create a TCP connection."""
        return self._loop.create_connection(protocol_factory, host, port, **kwargs)

    def create_unix_connection(self, protocol_factory: Callable, path: str, **kwargs) -> Coroutine:
        """Create a Unix domain socket connection."""
        return self._loop.create_unix_connection(protocol_factory, path, **kwargs)

    def create_datagram_endpoint(self, protocol_factory: Callable, local_addr=None, remote_addr=None, **kwargs) -> Coroutine:
        """Create a UDP endpoint."""
        return self._loop.create_datagram_endpoint(protocol_factory, local_addr=local_addr, remote_addr=remote_addr, **kwargs)

    async def open_connection(self, host: str = None, port: int = None, **kwargs) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Create a TCP connection returning a (reader, writer) pair."""
        return await asyncio.open_connection(host, port, loop=self._loop, **kwargs)

    async def start_server(self, client_connected_cb: Callable, host: str = None, port: int = None, **kwargs) -> asyncio.Server:
        """Start a TCP server."""
        return await asyncio.start_server(client_connected_cb, host, port, loop=self._loop, **kwargs)

    def add_signal_handler(self, sig: int, callback: Callable, *args) -> None:
        """Add a handler for a signal."""
        self._loop.add_signal_handler(sig, callback, *args)

    def remove_signal_handler(self, sig: int) -> bool:
        """Remove a handler for a signal."""
        return self._loop.remove_signal_handler(sig)

    async def subprocess_shell(self, cmd: str, **kwargs) -> asyncio.subprocess.Process:
        """Create a subprocess from a shell command."""
        return await asyncio.create_subprocess_shell(cmd, loop=self._loop, **kwargs)

    async def subprocess_exec(self, program: str, *args, **kwargs) -> asyncio.subprocess.Process:
        """Create a subprocess from program and arguments."""
        return await asyncio.create_subprocess_exec(program, *args, loop=self._loop, **kwargs)

    def set_exception_handler(self, handler: Optional[Callable[[str, Dict[str, Any]], Any]]) -> None:
        """Set exception handler for the event loop."""
        self._loop.set_exception_handler(handler)

    def get_exception_handler(self) -> Optional[Callable[[str, Dict[str, Any]], Any]]:
        """Get the current exception handler."""
        return self._loop.get_exception_handler()

    def default_exception_handler(self, context: Dict[str, Any]) -> None:
        """Default exception handler implementation."""
        self._loop.default_exception_handler(context)

    def call_exception_handler(self, context: Dict[str, Any]) -> None:
        """Call the current exception handler."""
        self._loop.call_exception_handler(context)

    async def sendfile(self, transport: asyncio.Transport, file: Any, offset: int = 0, count: Optional[int] = None) -> int:
        """Send a file over transport."""
        return await self._loop.sendfile(transport, file, offset, count)

    def set_task_factory(self, factory: Optional[Callable[[asyncio.AbstractEventLoop, asyncio.Future], asyncio.Task]]) -> None:
        """Set task factory for creating new tasks."""
        self._loop.set_task_factory(factory)

    def get_task_factory(self) -> Optional[Callable[[asyncio.AbstractEventLoop, asyncio.Future], asyncio.Task]]:
        """Get the current task factory."""
        return self._loop.get_task_factory()

    def is_closed(self) -> bool:
        """Return True if the event loop is closed."""
        return self._loop.is_closed()

    def is_running(self) -> bool:
        """Return True if the event loop is running."""
        return self._loop.is_running()

    def stop(self) -> None:
        """Stop the event loop."""
        self._loop.stop()

    def close(self) -> None:
        """Close the event loop."""
        self._loop.close()

    def shutdown_asyncgens(self) -> Coroutine:
        """Shutdown async generators."""
        return self._loop.shutdown_asyncgens()

    def shutdown_default_executor(self) -> Coroutine:
        """Shutdown the default executor."""
        return self._loop.shutdown_default_executor()

    async def _handle_cancellation(self) -> None:
        """Handle task cancellation with proper cleanup."""
        logging.debug(f"Task {self.name} cancelled")
        for callback in self._cleanup_callbacks:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logging.error(f"Error in cancellation callback: {e}")
    
    async def _handle_error(self, error: Exception) -> None:
        """Handle task errors with proper propagation and logging."""
        logging.error(f"Task {self.name} failed: {error}")
        self._info.debug_info['traceback'] = traceback.format_exc()
        
        if self.parent:
            self.parent._info.debug_info[f'child_error_{self.name}'] = str(error)

    @property
    def debug(self) -> bool:
        """Get debug mode status."""
        return self._loop.get_debug()

    @debug.setter
    def debug(self, enabled: bool) -> None:
        """Set debug mode."""
        self._loop.set_debug(enabled)

    def get_debug(self) -> bool:
        """Get debug mode status."""
        return self._loop.get_debug()

    def set_debug(self, enabled: bool) -> None:
        """Set debug mode."""
        self._loop.set_debug(enabled)

    def time(self) -> float:
        """Return current time according to event loop's clock."""
        return self._loop.time()

    def set_slow_callback_duration(self, duration: float) -> None:
        """Set duration threshold for slow callback warnings."""
        if hasattr(self._loop, 'slow_callback_duration'):
            self._loop.slow_callback_duration = duration

    def get_slow_callback_duration(self) -> Optional[float]:
        """Get duration threshold for slow callback warnings."""
        return getattr(self._loop, 'slow_callback_duration', None)

    async def connect_read_pipe(self, protocol_factory: Callable[[], asyncio.Protocol], pipe: Any) -> tuple:
        """Connect read end of a pipe."""
        return await self._loop.connect_read_pipe(protocol_factory, pipe)

    async def connect_write_pipe(self, protocol_factory: Callable[[], asyncio.Protocol], pipe: Any) -> tuple:
        """Connect write end of a pipe."""
        return await self._loop.connect_write_pipe(protocol_factory, pipe)

    def add_reader(self, fd: Union[int, Any], callback: Callable, *args: Any) -> None:
        """Add a reader callback for a file descriptor."""
        self._loop.add_reader(fd, callback, *args)

    def remove_reader(self, fd: Union[int, Any]) -> bool:
        """Remove reader callback for a file descriptor."""
        return self._loop.remove_reader(fd)

    def add_writer(self, fd: Union[int, Any], callback: Callable, *args: Any) -> None:
        """Add a writer callback for a file descriptor."""
        self._loop.add_writer(fd, callback, *args)

    def remove_writer(self, fd: Union[int, Any]) -> bool:
        """Remove writer callback for a file descriptor."""
        return self._loop.remove_writer(fd)

    async def sock_recv(self, sock: Any, nbytes: int) -> bytes:
        """Receive data from a socket."""
        return await self._loop.sock_recv(sock, nbytes)

    async def sock_recv_into(self, sock: Any, buf: Any) -> int:
        """Receive data from a socket into a buffer."""
        return await self._loop.sock_recv_into(sock, buf)

    async def sock_sendall(self, sock: Any, data: bytes) -> None:
        """Send data to a socket."""
        await self._loop.sock_sendall(sock, data)

    async def sock_connect(self, sock: Any, address: Any) -> None:
        """Connect to a remote socket."""
        await self._loop.sock_connect(sock, address)

    async def sock_accept(self, sock: Any) -> tuple[Any, Any]:
        """Accept a connection on a socket."""
        return await self._loop.sock_accept(sock)

    async def sock_sendfile(self, sock: Any, file: Any, offset: int = 0, count: Optional[int] = None, 
                          *, fallback: bool = True) -> int:
        """Send a file through a socket."""
        return await self._loop.sock_sendfile(sock, file, offset, count, fallback=fallback)

    @classmethod
    def create_group(cls, *tasks: 'Asyn') -> 'Asyn':
        """Create a group of tasks with a common parent."""
        group = cls(name="TaskGroup")
        for task in tasks:
            task._info.parent = group
            group.children.add(task)
        return group
    
    def get_task_tree(self) -> Dict[str, Any]:
        """Get a hierarchical representation of the task tree."""
        tree = {
            'name': self.name,
            'state': self.state.value,
            'children': []
        }
        
        for child in self.children:
            tree['children'].append(child.get_task_tree())
        
        return tree
    
    async def wait_for_children(self) -> None:
        """Wait for all child tasks to complete."""
        if self.children:
            await asyncio.gather(*(
                child.info.task for child in self.children
                if child.info.task and not child.info.task.done()
            ))
    
    def __repr__(self) -> str:
        return f"Asyn(name={self.name}, state={self.state}, children={len(self.children)})"

    @classmethod
    async def gather(cls, *coros_or_tasks, return_exceptions=False) -> Tuple[Any]:
        """Enhanced gather that maintains task relationships and error handling."""
        tasks = [
            coro if isinstance(coro, Asyn) else cls(name=f"gathered-{i}").run(coro)
            for i, coro in enumerate(coros_or_tasks)
        ]
        return await asyncio.gather(*tasks, return_exceptions=return_exceptions)

    @classmethod
    async def wait(cls, tasks: Set['Asyn'], *, timeout: Optional[float] = None,
                  return_when=asyncio.ALL_COMPLETED) -> tuple[Set['Asyn'], Set['Asyn']]:
        """Enhanced wait with Python 3.11+ return type hints."""
        raw_tasks = {task._info.task for task in tasks if task._info.task}
        done, pending = await asyncio.wait(raw_tasks, timeout=timeout, return_when=return_when)
        done_tasks = {task for task in tasks if task._info.task in done}
        pending_tasks = {task for task in tasks if task._info.task in pending}
        return done_tasks, pending_tasks

    @classmethod
    async def shield(cls, coro_or_task: Union[Coroutine, 'Asyn']) -> Any:
        """Shield a coroutine or task from cancellation."""
        if isinstance(coro_or_task, Asyn):
            return await asyncio.shield(coro_or_task._info.task)
        task = cls(name="shielded")
        return await asyncio.shield(task.run(coro_or_task))

    @classmethod
    async def wait_for(cls, coro_or_task: Union[Coroutine, 'Asyn'], 
                      timeout: Optional[float]) -> Any:
        """Wait for a coroutine with timeout."""
        if isinstance(coro_or_task, Asyn):
            return await asyncio.wait_for(coro_or_task._info.task, timeout)
        task = cls(name="timeout-task")
        return await asyncio.wait_for(task.run(coro_or_task), timeout)

    async def as_completed(self, timeout: Optional[float] = None) -> Any:
        """Yield completed child tasks as they finish."""
        raw_tasks = {child.info.task for child in self.children if child.info.task}
        for done_task in asyncio.as_completed(raw_tasks, timeout=timeout):
            task_result = await done_task
            yield task_result

    def get_running_loop(self) -> asyncio.AbstractEventLoop:
        """Get the running event loop."""
        return self._loop or asyncio.get_running_loop()

    async def _legacy_timeout(self, delay: Optional[float]) -> AsyncIterator[None]:
        """Legacy implementation of timeout for Python < 3.11."""
        timer = None
        try:
            if delay is not None:
                timer = self._loop.call_later(delay, self.cancel)
            yield
        finally:
            if timer is not None:
                timer.cancel()

    @requires_py311(fallback=_legacy_timeout)
    async def timeout(self, delay: Optional[float]) -> AsyncIterator[None]:
        """Enhanced timeout context manager with Python 3.11+ compatibility."""
        async with asyncio.timeout(delay):
            yield

    async def _legacy_timeout_at(self, deadline: float) -> AsyncIterator[None]:
        """Legacy implementation of timeout_at for Python < 3.11."""
        now = self._loop.time()
        timeout = max(0, int(deadline - now))
        async with asyncio.timeout(timeout):
            yield

    @requires_py311(fallback=_legacy_timeout_at)
    async def timeout_at(self, deadline: float) -> AsyncIterator[None]:
        """Context manager for absolute timeouts (Python 3.11+)."""
        async with asyncio.timeout_at(deadline):
            yield

    async def _legacy_with_timeout(self, delay: Optional[float], coro: Coroutine[Any, Any, T]) -> T:
        """Legacy implementation of with_timeout for Python < 3.11."""
        async with self.timeout(delay):
            return await coro

    @requires_py311(fallback=_legacy_with_timeout)
    def with_timeout(self, delay: Optional[float]) -> T:
        """Run a coroutine with timeout (Python 3.11+ style)."""
        return asyncio.timeout(delay)

    @contextmanager
    def debug_context(self):
        """Context manager for adding debug information to the task."""
        try:
            yield self._info.debug_info
        finally:
            if self._info.debug_info:
                logging.debug(f"Debug info for {self.name}: {self._info.debug_info}")

class AsyncTaskGroup:
    """Enhanced version of asyncio.TaskGroup with structured task management."""
    
    def __init__(self, parent: Optional['Asyn'] = None):
        self._parent = parent
        self._tasks: Set[Asyn] = set()
        self._exit_stack = AsyncExitStack()
        self._active = False
        self._native_group = None

    # noinspection PyCompatibility
    async def _legacy_create_task(self, coro: Coroutine[Any, Any, T], *, name: Optional[str] = None) -> T:
        """Legacy implementation of create_task for Python < 3.11."""
        asyn_task = Asyn(name=name or f"grouped-{len(self._tasks)}", parent=self._parent)
        self._tasks.add(asyn_task)
        try:
            return await asyn_task.run(coro)
        except* Exception as eg:
            raise ExceptionGroup("Task group exceptions", eg.exceptions)

    @requires_py311(fallback=_legacy_create_task)
    async def create_task(self, coro: Coroutine[Any, Any, T], *, name: Optional[str] = None) -> T:
        """Create a new task in the group."""
        if not self._active:
            raise RuntimeError("AsyncTaskGroup is not active")
        
        task = self._native_group.create_task(coro, name=name)
        asyn_task = Asyn(name=name or f"grouped-{len(self._tasks)}", parent=self._parent)
        asyn_task.info.task = task
        self._tasks.add(asyn_task)
        return await task

    async def _legacy_aenter(self) -> 'AsyncTaskGroup':
        """Legacy implementation of __aenter__ for Python < 3.11."""
        self._active = True
        await self._exit_stack.__aenter__()
        return self

    @requires_py311(fallback=_legacy_aenter)
    async def __aenter__(self) -> 'AsyncTaskGroup':
        """Enter the task group context."""
        self._active = True
        await self._exit_stack.__aenter__()
        self._native_group = await self._exit_stack.enter_async_context(asyncio.TaskGroup())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._active = False
        await self._exit_stack.__aexit__(exc_type, exc_val, exc_tb)
