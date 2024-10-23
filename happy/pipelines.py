# Define custom exceptions
import asyncio
import concurrent.futures
import logging
import queue
import threading
import time
from collections import defaultdict
from contextlib import contextmanager, asynccontextmanager, AbstractContextManager
from multiprocessing import RLock
from multiprocessing import Pool as MPPool
from typing import Optional, List, Callable, Any, Coroutine, Dict, TypeVar, Union, Generic
from multiprocessing import Process, Queue as MPQueue
from happy.exceptions import TransactionError, TransactionCommitError, TransactionRollbackError, EventDispatchError, \
    HandlerNotFound, HandlerAlreadyRegistered, PoolException, PoolShutdownException, PoolTimeoutException, \
    InvalidPipelineStepException, PipelineExecutionException
from happy.protocols import LoggerProtocol, NullLogger, ThreadingProtocol, MultiprocessingProtocol, ResourceFactory, \
    DefaultThreadPoolExecutor, DefaultProcessPoolExecutor, PipelineStepProtocol

T = TypeVar('T')


class Transaction:
    def __init__(
            self,
            enable_logging: bool = False,
            logger: Optional[LoggerProtocol] = None,
            loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        self._operations: List[Callable[[], Any]] = []
        self._async_operations: List[Callable[[], Coroutine[Any, Any, Any]]] = []
        self._lock = RLock()
        self._active = False
        self._logger = logger or self._configure_default_logger() if enable_logging else None
        self._savepoints: List[Dict[str, List]] = []
        self._commit_callbacks: List[Callable[[], Any]] = []
        self._rollback_callbacks: List[Callable[[], Any]] = []
        self._loop = loop or asyncio.get_event_loop()
        self._traceback = {}  # TODO: implement

    @staticmethod
    def _configure_default_logger() -> LoggerProtocol:
        logger = logging.getLogger('TransactionLogger')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def begin(self):
        with self._lock:
            if self._active:
                if self._logger:
                    self._logger.warning("Nested transactions are not supported directly. Use savepoints.")
                raise TransactionError("Transaction already active. Use savepoints for nested transactions.")
            self._active = True
            self._operations = []
            self._async_operations = []
            self._savepoints = []
            if self._logger:
                self._logger.info("Transaction started.")

    async def begin_async(self):
        self.begin()

    def commit(self):
        with self._lock:
            if not self._active:
                raise TransactionError("No active transaction to commit.")
            try:
                for operation in self._operations:
                    operation()
                for async_op in self._async_operations:
                    if asyncio.iscoroutinefunction(async_op):
                        self._loop.run_until_complete(async_op())
                    else:
                        async_op()
                for callback in self._commit_callbacks:
                    callback()
                self._active = False
                self._operations.clear()
                self._async_operations.clear()
                self._savepoints.clear()
                if self._logger:
                    self._logger.info("Transaction committed successfully.")
            except Exception as e:
                self._active = False
                self._operations.clear()
                self._async_operations.clear()
                self._savepoints.clear()
                if self._logger:
                    self._logger.error(f"Transaction failed to commit: {e}")
                raise TransactionCommitError(f"Failed to commit transaction: {e}") from e

    async def commit_async(self):
        async with self._lock_async():
            if not self._active:
                raise TransactionError("No active transaction to commit.")
            try:
                for operation in self._operations:
                    operation()
                for async_op in self._async_operations:
                    if asyncio.iscoroutinefunction(async_op):
                        await async_op()
                    else:
                        async_op()
                for callback in self._commit_callbacks:
                    if asyncio.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
                self._active = False
                self._operations.clear()
                self._async_operations.clear()
                self._savepoints.clear()
                if self._logger:
                    self._logger.info("Transaction committed successfully.")
            except Exception as e:
                self._active = False
                self._operations.clear()
                self._async_operations.clear()
                self._savepoints.clear()
                if self._logger:
                    self._logger.error(f"Transaction failed to commit: {e}")
                raise TransactionCommitError(f"Failed to commit transaction: {e}") from e

    def rollback(self):
        with self._lock:
            if not self._active:
                raise TransactionError("No active transaction to rollback.")
            try:
                for callback in self._rollback_callbacks:
                    callback()
                self._active = False
                self._operations.clear()
                self._async_operations.clear()
                self._savepoints.clear()
                if self._logger:
                    self._logger.info("Transaction rolled back.")
            except Exception as e:
                if self._logger:
                    self._logger.error(f"Transaction failed to rollback: {e}")
                raise TransactionRollbackError(f"Failed to rollback transaction: {e}") from e

    async def rollback_async(self):
        async with self._lock_async():
            if not self._active:
                raise TransactionError("No active transaction to rollback.")
            try:
                for callback in self._rollback_callbacks:
                    if asyncio.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
                self._active = False
                self._operations.clear()
                self._async_operations.clear()
                self._savepoints.clear()
                if self._logger:
                    self._logger.info("Transaction rolled back.")
            except Exception as e:
                if self._logger:
                    self._logger.error(f"Transaction failed to rollback: {e}")
                raise TransactionRollbackError(f"Failed to rollback transaction: {e}") from e

    def add_operation(self, operation: Callable[[], Any]):
        with self._lock:
            if not self._active:
                raise TransactionError("No active transaction. Call begin() before adding operations.")
            self._operations.append(operation)
            if self._logger:
                self._logger.debug(f"Operation added: {operation}")

    def add_async_operation(self, operation: Callable[[], Coroutine[Any, Any, Any]]):
        with self._lock:
            if not self._active:
                raise TransactionError("No active transaction. Call begin() before adding operations.")
            self._async_operations.append(operation)
            if self._logger:
                self._logger.debug(f"Async operation added: {operation}")

    @contextmanager
    def savepoint(self):
        with self._lock:
            if not self._active:
                raise TransactionError("No active transaction to create a savepoint.")
            savepoint = {
                'operations': list(self._operations),
                'async_operations': list(self._async_operations)
            }
            self._savepoints.append(savepoint)
            if self._logger:
                self._logger.info("Savepoint created.")
            try:
                yield
            except Exception as e:
                last_savepoint = self._savepoints.pop()
                self._operations = last_savepoint['operations']
                self._async_operations = last_savepoint['async_operations']
                if self._logger:
                    self._logger.info("Rolled back to the last savepoint.")
                raise e

    @asynccontextmanager
    async def async_savepoint(self):
        async with self._lock_async():
            if not self._active:
                raise TransactionError("No active transaction to create a savepoint.")
            savepoint = {
                'operations': list(self._operations),
                'async_operations': list(self._async_operations)
            }
            self._savepoints.append(savepoint)
            if self._logger:
                self._logger.info("Savepoint created.")
            try:
                yield
            except Exception as e:
                last_savepoint = self._savepoints.pop()
                self._operations = last_savepoint['operations']
                self._async_operations = last_savepoint['async_operations']
                if self._logger:
                    self._logger.info("Rolled back to the last savepoint.")
                raise e

    def register_commit_callback(self, callback: Callable[[], Any]):
        with self._lock:
            self._commit_callbacks.append(callback)
            if self._logger:
                self._logger.debug(f"Commit callback registered: {callback}")

    def register_rollback_callback(self, callback: Callable[[], Any]):
        with self._lock:
            self._rollback_callbacks.append(callback)
            if self._logger:
                self._logger.debug(f"Rollback callback registered: {callback}")

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            try:
                self.commit()
            except TransactionError:
                self.rollback()
                raise

    async def __aenter__(self):
        await self.begin_async()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback_async()
        else:
            try:
                await self.commit_async()
            except TransactionError:
                await self.rollback_async()
                raise

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
        )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(active={self._active}, "
            f"operations={len(self._operations)}, "
            f"async_operations={len(self._async_operations)}, "
            f"savepoints={len(self._savepoints)})"
        )

    def is_active(self) -> bool:
        return self._active

    def operation_count(self) -> int:
        return len(self._operations) + len(self._async_operations)

    @contextmanager
    def lock(self):
        self._lock.acquire()
        try:
            yield
        finally:
            self._lock.release()

    @asynccontextmanager
    async def lock_async(self):
        await asyncio.to_thread(self._lock.acquire)
        try:
            yield
        finally:
            self._lock.release()

    @asynccontextmanager
    async def lock_async(self):
        await asyncio.to_thread(self._lock.acquire)
        try:
            yield
        finally:
            self._lock.release()


# Optional logging system
class PipelineLogger:
    """Custom logger for the pipeline with optional logging protocols."""
    def __init__(self, logger: Optional[LoggerProtocol] = None):
        self.logger = logger
        logging.basicConfig(level=logging.INFO)

    def log(self, message: str):
        if self.logger:
            self.logger.info(message)

# Pipeline class
class Pipeline:
    """A class that manages pipelines, optimizes, and enhances them."""
    def __init__(self, steps: Optional[List[PipelineStepProtocol]] = None, logger: Optional[PipelineLogger] = None):
        self.steps = steps or []
        self.logger = logger
        self.lock = threading.Lock()  # For thread safety
        self.pool = MPPool()  # For multiprocessing
        self.optimized = False
        self.jobs = []  # Queue for job handling

    def add_step(self, step: PipelineStepProtocol) -> None:
        """Add a step to the pipeline."""
        if not isinstance(step, PipelineStepProtocol):
            raise InvalidPipelineStepException("The step does not follow the required protocol.")
        with self.lock:
            self.steps.append(step)
        if self.logger:
            self.logger.log(f"Added step: {step}")

    def optimize(self) -> None:
        """Optimize the pipeline."""
        # Placeholder for optimization logic
        with self.lock:
            self.optimized = True
        if self.logger:
            self.logger.log("Pipeline optimized.")

    async def run(self, input_data: Any) -> Any:
        """Run the pipeline asynchronously."""
        if not self.steps:
            raise PipelineExecutionException("No steps to run in the pipeline.")

        data = input_data
        for step in self.steps:
            try:
                if self.logger:
                    self.logger.log(f"Running step: {step}")
                data = await step.run(data)
            except Exception as e:
                if self.logger:
                    self.logger.log(f"Step failed: {step} with error: {e}")
                raise PipelineExecutionException(f"Step {step} failed with error: {str(e)}") from e
        return data

    def run_sync(self, input_data: Any) -> Any:
        """Run the pipeline synchronously, using threading/multiprocessing where needed."""
        with self.lock:
            data = input_data
            for step in self.steps:
                try:
                    data = self.pool.apply(step.run, args=(data,))
                except Exception as e:
                    raise PipelineExecutionException(f"Step {step} failed with error: {str(e)}") from e
        return data

    def add_job(self, job: Callable) -> None:
        """Add a job to the pipeline."""
        with self.lock:
            self.jobs.append(job)
        if self.logger:
            self.logger.log(f"Job added: {job}")

    def execute_jobs(self) -> None:
        """Execute all queued jobs."""
        with self.lock:
            for job in self.jobs:
                job()
            self.jobs.clear()
        if self.logger:
            self.logger.log("Executed all jobs.")

    def __str__(self) -> str:
        return f"<Pipeline optimized={self.optimized}, steps={len(self.steps)}>"

    def __repr__(self) -> str:
        return f"Pipeline(steps={self.steps}, optimized={self.optimized})"

class PoolMetrics:
    """Class to hold metrics related to the Pool."""

    def __init__(self):
        self.total_acquires = 0
        self.total_releases = 0
        self.total_errors = 0
        self.acquisition_failures = 0
        self.release_failures = 0
        self.lock = threading.Lock()

    def increment_acquires(self):
        with self.lock:
            self.total_acquires += 1

    def increment_releases(self):
        with self.lock:
            self.total_releases += 1

    def increment_errors(self):
        with self.lock:
            self.total_errors += 1

    def increment_acquisition_failures(self):
        with self.lock:
            self.acquisition_failures += 1

    def increment_release_failures(self):
        with self.lock:
            self.release_failures += 1

    def get_metrics(self) -> Dict[str, int]:
        with self.lock:
            return {
                'total_acquires': self.total_acquires,
                'total_releases': self.total_releases,
                'total_errors': self.total_errors,
                'acquisition_failures': self.acquisition_failures,
                'release_failures': self.release_failures,
            }


class Pool(Generic[T]):

    def __init__(
            self,
            max_size: int,
            resource_factory = None,
            async_resource_factory = None,
            timeout = None,
            logger = None,
    ):
        if max_size <= 0:
            raise ValueError("max_size must be greater than 0")
        if not resource_factory and not async_resource_factory:
            raise ValueError("Either resource_factory or async_resource_factory must be provided")
        if resource_factory and async_resource_factory:
            raise ValueError("Provide only one of resource_factory or async_resource_factory, not both")

        self._max_size = max_size
        self._resource_factory = resource_factory
        self._async_resource_factory = async_resource_factory
        self._timeout = timeout
        self._logger = logger or logging.getLogger(__name__)

        # Internal queues and tracking
        self._available = (
            asyncio.Queue(maxsize=max_size) if self._async_resource_factory else queue.Queue(maxsize=max_size)
        )
        self._in_use: List[T] = []
        self._async_lock = asyncio.Lock()
        self._sync_lock = threading.Lock()
        self._shutdown = False
        self._closed = False

        # Callbacks
        self._on_acquire_callbacks = []
        self._on_release_callbacks = []
        self._on_error_callbacks = []

        # Metrics
        self._metrics = PoolMetrics()

        # Job queue for multiprocessing
        self._job_queue = None
        self._process = None

    async def _create_resource_async(self) -> T:
        if self._async_resource_factory is None:
            raise PoolException("Async resource factory not provided")
        resource = await self._async_resource_factory()
        self._logger.debug("Created new async resource: %s", resource)
        return resource

    def _create_resource(self) -> T:
        if self._resource_factory is None:
            raise PoolException("Resource factory not provided")
        resource = self._resource_factory()
        self._logger.debug("Created new resource: %s", resource)
        return resource

    async def acquire(self) -> T:
        async with self._async_lock:
            if self._shutdown:
                self._metrics.increment_acquisition_failures()
                raise PoolShutdownException("Cannot acquire from a shutdown pool")

            try:
                if self._timeout is not None:
                    resource = await asyncio.wait_for(self._available.get(), timeout=self._timeout)
                else:
                    resource = await self._available.get()
                self._logger.debug("Acquired resource from pool: %s", resource)
                self._metrics.increment_acquires()
            except asyncio.TimeoutError:
                self._logger.warning("Timeout while acquiring resource")
                self._metrics.increment_acquisition_failures()
                raise PoolTimeoutException("Timeout while acquiring resource")

            self._in_use.append(resource)

        for callback in self._on_acquire_callbacks:
            try:
                callback(resource)
            except Exception as e:
                self._handle_error(e)

        return resource

    def acquire_sync(self) -> T:
        if self._shutdown:
            self._metrics.increment_acquisition_failures()
            raise PoolShutdownException("Cannot acquire from a shutdown pool")
        try:
            if self._timeout is not None:
                resource = self._available.get(timeout=self._timeout)
            else:
                resource = self._available.get_nowait()
            self._logger.debug("Acquired resource from pool: %s", resource)
            self._metrics.increment_acquires()
        except queue.Empty:
            self._logger.warning("No available resources to acquire")
            self._metrics.increment_acquisition_failures()
            raise PoolTimeoutException("No available resources to acquire")

        with self._sync_lock:
            self._in_use.append(resource)

        for callback in self._on_acquire_callbacks:
            try:
                callback(resource)
            except Exception as e:
                self._handle_error(e)

        return resource

    async def release(self, resource: T) -> None:
        async with self._async_lock:
            if resource not in self._in_use:
                self._logger.error("Attempted to release unknown resource: %s", resource)
                self._metrics.increment_release_failures()
                raise PoolException("Attempted to release unknown resource")
            self._in_use.remove(resource)
            await self._available.put(resource)
            self._logger.debug("Released resource back to pool: %s", resource)
            self._metrics.increment_releases()

        for callback in self._on_release_callbacks:
            try:
                callback(resource)
            except Exception as e:
                self._handle_error(e)

    def release_sync(self, resource: T) -> None:
        with self._sync_lock:
            if resource not in self._in_use:
                self._logger.error("Attempted to release unknown resource: %s", resource)
                self._metrics.increment_release_failures()
                raise PoolException("Attempted to release unknown resource")
            self._in_use.remove(resource)
            self._available.put_nowait(resource)
            self._logger.debug("Released resource back to pool: %s", resource)
            self._metrics.increment_releases()

        for callback in self._on_release_callbacks:
            try:
                callback(resource)
            except Exception as e:
                self._handle_error(e)

    async def initialize(self) -> None:
        async with self._async_lock:
            for _ in range(self._max_size):
                if self._async_resource_factory:
                    resource = await self._create_resource_async()
                else:
                    resource = self._create_resource()
                await self._available.put(resource)
            self._logger.info("Initialized pool with %d resources", self._max_size)

    def initialize_sync(self) -> None:
        with self._sync_lock:
            for _ in range(self._max_size):
                resource = self._create_resource()
                self._available.put_nowait(resource)
            self._logger.info("Initialized pool with %d resources", self._max_size)

    async def shutdown_pool(self, wait: bool = True) -> None:
        async with self._async_lock:
            self._shutdown = True
            self._logger.info("Shutting down pool")

        if wait:
            while True:
                async with self._async_lock:
                    if not self._in_use:
                        break
                await asyncio.sleep(0.1)  # Wait briefly before checking again

        # Close available resources
        while not self._available.empty():
            resource = await self._available.get()
            await self._close_resource(resource)

        self._logger.info("Pool shutdown complete")
        self._closed = True

    def shutdown_pool_sync(self, wait: bool = True) -> None:
        with self._sync_lock:
            self._shutdown = True
            self._logger.info("Shutting down pool")

        if wait:
            while True:
                with self._sync_lock:
                    if not self._in_use:
                        break
                time.sleep(0.1)  # Wait briefly before checking again

        # Close available resources
        while not self._available.empty():
            resource = self._available.get_nowait()
            self._close_resource_sync(resource)

        self._logger.info("Pool shutdown complete")
        self._closed = True

    async def _close_resource(self, resource: T) -> None:
        self._logger.debug("Closing resource: %s", resource)
        close_method = getattr(resource, "close", None)
        if callable(close_method):
            try:
                if asyncio.iscoroutinefunction(close_method):
                    await close_method()
                else:
                    close_method()
            except Exception as e:
                self._handle_error(e)

    def _close_resource_sync(self, resource: T) -> None:
        self._logger.debug("Closing resource: %s", resource)
        close_method = getattr(resource, "close", None)
        if callable(close_method):
            try:
                close_method()
            except Exception as e:
                self._handle_error(e)

    @contextmanager
    def context_acquire(self) -> T:
        resource = self.acquire_sync()
        try:
            yield resource
        finally:
            self.release_sync(resource)

    @asynccontextmanager
    async def async_context_acquire(self) -> T:
        resource = await self.acquire()
        try:
            yield resource
        finally:
            await self.release(resource)

    def __repr__(self) -> str:
        available_size = self._available.qsize() if isinstance(self._available,
                                                               queue.Queue) else self._available.qsize()
        return (
            f"<Pool size={self._max_size} available={available_size} "
            f"in_use={len(self._in_use)} shutdown={self._shutdown}>"
        )

    def register_on_acquire(self, callback) -> None:
        self._on_acquire_callbacks.append(callback)
        self._logger.debug("Registered on_acquire callback.")

    def register_on_release(self, callback) -> None:
        self._on_release_callbacks.append(callback)
        self._logger.debug("Registered on_release callback.")

    def register_on_error(self, callback) -> None:
        self._on_error_callbacks.append(callback)
        self._logger.debug("Registered on_error callback.")

    def _handle_error(self, exception: Exception) -> None:
        self._logger.error(f"Error in callback: {exception}")
        self._metrics.increment_errors()
        for callback in self._on_error_callbacks:
            try:
                callback(exception)
            except Exception as e:
                self._logger.error(f"Error in error callback: {e}")

    def get_status(self) -> Dict[str, Union[int, bool]]:
        with self._sync_lock:
            status = {
                'max_size': self._max_size,
                'current_available': self._available.qsize(),
                'in_use': len(self._in_use),
                'shutdown': self._shutdown,
                'closed': self._closed,
            }
        metrics = self._metrics.get_metrics()
        status.update(metrics)
        self._logger.debug(f"Pool status: {status}")
        return status

    def resize(self, new_size: int) -> None:
        with self._sync_lock:
            if new_size <= 0:
                raise ValueError("New size must be greater than 0.")
            if new_size < len(self._in_use):
                raise ValueError("New size cannot be less than the number of resources in use.")
            difference = new_size - self._max_size
            if difference > 0:
                # Increase pool size by adding new resources
                for _ in range(difference):
                    resource = self._create_resource()
                    self._available.put_nowait(resource)
            elif difference < 0:
                # Decrease pool size by removing available resources
                for _ in range(-difference):
                    try:
                        resource = self._available.get_nowait()
                        self._close_resource_sync(resource)
                    except queue.Empty:
                        self._logger.warning("No more available resources to remove during resize.")
                        break
            self._max_size = new_size
            self._available._maxsize = new_size  # Adjust the queue's maxsize
            self._logger.debug(f"Pool resized to max_size={self._max_size}.")

    def submit_job(self, job, *args, **kwargs):
        if self._shutdown:
            raise PoolShutdownException("Cannot submit jobs to a shutdown pool")

        def wrapper():
            with self.context_acquire() as resource:
                return job(resource, *args, **kwargs)

        thread = threading.Thread(target=wrapper)
        thread.start()
        thread.join()
        # Note: For more sophisticated job handling, consider returning futures or using a thread pool.

    def start_multiprocessing_pool(self, worker_function: Callable, *args, **kwargs) -> None:
        if self._process and self._process.is_alive():
            self._logger.warning("Multiprocessing pool is already running.")
            return

        self._job_queue = MPQueue()
        self._process = Process(target=self._worker_process, args=(worker_function, self._job_queue, *args),
                                kwargs=kwargs)
        self._process.start()
        self._logger.info("Started multiprocessing pool.")

    def _worker_process(self, worker_function: Callable, job_queue: MPQueue):
        while True:
            try:
                job, job_args, job_kwargs = job_queue.get()
                if job is None:
                    break  # Sentinel to shut down
                worker_function(job, *job_args, **job_kwargs)
            except Exception as e:
                self._handle_error(e)

    def submit_multiprocessing_job(self, job, *args, **kwargs) -> None:
        if not self._job_queue:
            raise PoolException("Multiprocessing pool is not initialized.")
        self._job_queue.put((job, args, kwargs))
        self._logger.debug("Submitted job to multiprocessing pool.")

    def shutdown_multiprocessing_pool(self) -> None:
        if self._job_queue and self._process:
            self._job_queue.put((None, (), {}))  # Sentinel to shut down
            self._process.join()
            self._logger.info("Multiprocessing pool shutdown complete.")
            self._job_queue = None
            self._process = None

    def get_metrics(self) -> Dict[str, int]:
        return self._metrics.get_metrics()

    def health_check(self, check_function: Callable[[T], bool], interval: float = 60.0) -> None:
        def monitor():
            while not self._shutdown:
                with self._sync_lock:
                    for resource in list(self._available.queue):
                        if not check_function(resource):
                            self._available.get()
                            self._close_resource_sync(resource)
                            new_resource = self._create_resource()
                            self._available.put_nowait(new_resource)
                            self._logger.info("Replaced faulty resource.")
                time.sleep(interval)

        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        self._logger.info("Started health monitoring thread.")

class EventListener(AbstractContextManager):
    def __init__(
            self,
            logger: Optional[LoggerProtocol] = None,
            threading_executor: Optional[ThreadingProtocol] = None,
            multiprocessing_executor: Optional[MultiprocessingProtocol] = None,
    ):
        self._handlers: Dict[str, List[Callable[..., Union[Any, Coroutine[Any, Any, Any]]]]] = defaultdict(list)
        self._logger: LoggerProtocol = logger if logger is not None else NullLogger()
        self._active = False
        self._lock = threading.RLock()
        self._threading_executor = threading_executor if threading_executor is not None else DefaultThreadPoolExecutor()
        self._multiprocessing_executor = multiprocessing_executor if multiprocessing_executor is not None else DefaultProcessPoolExecutor()

    def register(
            self,
            event: str,
            handler: Callable[..., Union[Any, Coroutine[Any, Any, Any]]],
            run_in_thread: bool = False,
            run_in_process: bool = False
    ) -> None:
        with self._lock:
            if handler in self._handlers[event]:
                raise HandlerAlreadyRegistered(f"Handler {handler} is already registered for event '{event}'.")
            self._handlers[event].append(handler)
            self._logger.info(
                f"Handler {handler} registered for event '{event}'. Run in thread: {run_in_thread}, Run in process: {run_in_process}.")
            # Store handler options
            if not hasattr(handler, '_run_in_thread'):
                setattr(handler, '_run_in_thread', run_in_thread)
            if not hasattr(handler, '_run_in_process'):
                setattr(handler, '_run_in_process', run_in_process)

    def deregister(self, event: str, handler: Callable[..., Any]) -> None:
        with self._lock:
            if handler not in self._handlers[event]:
                raise HandlerNotFound(f"Handler {handler} not found for event '{event}'.")
            self._handlers[event].remove(handler)
            self._logger.info(f"Handler {handler} deregistered from event '{event}'.")

    async def dispatch(self, event: str, *args, **kwargs) -> None:
        handlers = []
        with self._lock:
            handlers = list(self._handlers[event])  # Make a copy to prevent modification during iteration

        if not handlers:
            self._logger.warning(f"No handlers registered for event '{event}'.")
            return

        self._logger.info(f"Dispatching event '{event}' to {len(handlers)} handlers.")
        errors = []
        loop = asyncio.get_running_loop()
        futures = []

        for handler in handlers:
            try:
                if getattr(handler, '_run_in_process', False):
                    future = self._multiprocessing_executor.submit(handler, *args, **kwargs)
                    futures.append(future)
                elif getattr(handler, '_run_in_thread', False):
                    future = self._threading_executor.submit(handler, *args, **kwargs)
                    futures.append(future)
                else:
                    if asyncio.iscoroutinefunction(handler):
                        futures.append(handler(*args, **kwargs))
                    else:
                        handler(*args, **kwargs)
            except Exception as e:
                self._logger.error(f"Error scheduling handler {handler} for event '{event}': {e}")
                errors.append(e)

        # Wait for all futures to complete
        for future in futures:
            try:
                if isinstance(future, asyncio.Future):
                    await future
                elif isinstance(future, concurrent.futures.Future):
                    await loop.run_in_executor(None, future.result)
            except Exception as e:
                self._logger.error(f"Error in handler during dispatch for event '{event}': {e}")
                errors.append(e)

        if errors:
            raise EventDispatchError(errors)

    def _log_debug(self, msg: str) -> None:
        self._logger.debug(msg)

    def _log_info(self, msg: str) -> None:
        self._logger.info(msg)

    def _log_warning(self, msg: str) -> None:
        self._logger.warning(msg)

    def _log_error(self, msg: str) -> None:
        self._logger.error(msg)

    def _log_critical(self, msg: str) -> None:
        self._logger.critical(msg)

    async def __aenter__(self) -> 'EventListener':
        with self._lock:
            self._active = True
            self._logger.info("EventListener activated (async).")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        with self._lock:
            self._active = False
            self._logger.info("EventListener deactivated (async).")
            if exc_type:
                self._logger.error(f"Exception {exc_type} occurred: {exc_val}")

    def __enter__(self) -> 'EventListener':
        with self._lock:
            self._active = True
            self._logger.info("EventListener activated.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        with self._lock:
            self._active = False
            self._logger.info("EventListener deactivated.")
            if exc_type:
                self._logger.error(f"Exception {exc_type} occurred: {exc_val}")

    def shutdown(self, wait: bool = True) -> None:
        """Shuts down the executors."""
        self._threading_executor.shutdown(wait=wait)
        self._multiprocessing_executor.shutdown(wait=wait)
        self._logger.info("EventListener executors have been shut down.")
