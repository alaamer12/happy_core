Toolkits Module
===============

.. module:: happy_core.toolkits
  :no-index:

A comprehensive collection of utilities and decorators for enhancing code quality, performance, and maintainability.

Key Features
------------

- **Performance optimization** tools
- **Error handling** decorators
- **Monitoring and metrics** collection
- **Caching** mechanisms
- **Retry logic** with backoff strategies

Decorators
----------

retry
~~~~~

.. py:decorator:: retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: Tuple[Type[Exception], ...] = (Exception,))
   Robust retry mechanism with exponential backoff.

   **Key Features:**
   
   - Exponential backoff
   - Custom exception handling
   - Retry count tracking
   - Logging integration
   
   .. code-block:: python

      from happy_core.toolkits import retry
      
      @retry(max_attempts=3, delay=1, backoff=2)
      def fetch_data(url: str) -> dict:
          """Fetch data with automatic retry on failure."""
          response = requests.get(url)
          response.raise_for_status()
          return response.json()
      
      # With custom exceptions
      @retry(exceptions=(ConnectionError, TimeoutError))
      def connect_database():
          return db.connect()

monitor
~~~~~~~

.. py:decorator:: monitor(name: Optional[str] = None, metrics: Optional[List[str]] = None)

   Comprehensive function monitoring.

   **Capabilities:**
   
   - Execution time tracking
   - Memory usage monitoring
   - Error rate tracking
   - Custom metrics collection
   
   .. code-block:: python

      from happy_core.toolkits import monitor
      
      @monitor(metrics=["execution_time", "memory_usage"])
      def process_large_dataset(data: pd.DataFrame) -> pd.DataFrame:
          """Process data with performance monitoring."""
          return data.groupby("category").agg(metrics)
      
      # With custom metric
      @monitor(metrics=["rows_processed"])
      def transform_data(data: pd.DataFrame) -> pd.DataFrame:
          monitor.record("rows_processed", len(data))
          return data.transform(transform_func)

cache
~~~~~

.. py:decorator:: cache(ttl: int = 3600, max_size: int = 1000, strategy: str = "lru")

   Flexible caching mechanism with multiple strategies.

   **Features:**
   
   - Multiple cache strategies (LRU, LFU)
   - Time-based expiration
   - Size limits
   - Cache statistics
   
   .. code-block:: python

      from happy_core.toolkits import cache
      
      @cache(ttl=3600, strategy="lru")
      def expensive_calculation(x: int) -> float:
          """Cache expensive calculation results."""
          return sum(math.sin(i) for i in range(x))
      
      # With custom key function
      @cache(key_func=lambda x: f"data_{x['id']}")
      def fetch_user_data(user_info: dict) -> dict:
          return database.get_user(user_info["id"])

Utilities
---------

PerformanceTracker
~~~~~~~~~~~~~~~~~~

.. py:class:: PerformanceTracker

   Track and analyze performance metrics.

   **Capabilities:**
   
   - Real-time monitoring
   - Statistical analysis
   - Threshold alerts
   - Custom metrics
   
   .. code-block:: python

      from happy_core.toolkits import PerformanceTracker
      
      tracker = PerformanceTracker()
      
      with tracker.track("database_query"):
          results = db.execute_query(query)
      
      # Get statistics
      stats = tracker.get_statistics("database_query")
      print(f"Average query time: {stats.mean:.2f}s")

ErrorHandler
~~~~~~~~~~~~

.. py:class:: ErrorHandler

   Comprehensive error handling and logging.

   **Features:**
   
   - Error categorization
   - Custom handlers
   - Error aggregation
   - Notification integration
   
   .. code-block:: python

      from happy_core.toolkits import ErrorHandler
      
      handler = ErrorHandler()
      
      @handler.catch(notify=True)
      def critical_operation():
          # Your code here
          pass
      
      # Custom error handling
      handler.on_error(DatabaseError, lambda e: cleanup_connection())

Best Practices
--------------

1. **Retry Strategy**

   Choose appropriate retry parameters:

   .. code-block:: python

      # Good - specific exceptions with reasonable retry
      @retry(
          max_attempts=3,
          exceptions=(ConnectionError, TimeoutError),
          delay=1
      )
      def network_operation():
          pass
      
      # Bad - too many retries, generic exception
      @retry(max_attempts=10)
      def any_operation():
          pass

2. **Monitoring Usage**

   Monitor critical operations:

   .. code-block:: python

      # Good - specific metrics
      @monitor(metrics=["execution_time", "memory_usage"])
      def process_data():
          pass
      
      # Better - with custom metrics
      @monitor(metrics=["processed_items"])
      def batch_process(items):
          monitor.record("processed_items", len(items))
          for item in items:
              process_item(item)

3. **Cache Configuration**

   Configure cache appropriately:

   .. code-block:: python

      # Good - specific TTL and size limit
      @cache(ttl=3600, max_size=1000)
      def get_user_preferences(user_id: int) -> dict:
          return db.fetch_preferences(user_id)
      
      # Bad - infinite cache
      @cache()
      def accumulate_data(data: list) -> dict:
          return process_data(data)

Advanced Usage
--------------

1. **Custom Monitoring**

   Create specialized monitoring:

   .. code-block:: python

      class APIMonitor:
          def __init__(self):
              self.tracker = PerformanceTracker()
          
          def track_endpoint(self, endpoint: str):
              def decorator(func):
                  @monitor(name=f"api_{endpoint}")
                  def wrapped(*args, **kwargs):
                      with self.tracker.track(endpoint):
                          return func(*args, **kwargs)
                  return wrapped
              return decorator

2. **Smart Caching**

   Implement advanced caching:

   .. code-block:: python

      class SmartCache:
          def __init__(self, base_ttl: int = 3600):
              self.base_ttl = base_ttl
          
          def adaptive_cache(self, hit_multiplier: float = 1.5):
              def decorator(func):
                  @cache(ttl=self.base_ttl)
                  def wrapped(*args, **kwargs):
                      result = func(*args, **kwargs)
                      if cache.hit_rate > 0.8:
                          # Increase TTL for frequently accessed items
                          cache.update_ttl(self.base_ttl * hit_multiplier)
                      return result
                  return wrapped
              return decorator

3. **Error Recovery**

   Implement sophisticated error recovery:

   .. code-block:: python

      class RecoveryManager:
          def __init__(self):
              self.error_handler = ErrorHandler()
              self.recovery_strategies = {}
          
          def register_strategy(self, error_type: Type[Exception]):
              def decorator(strategy_func):
                  self.recovery_strategies[error_type] = strategy_func
                  return strategy_func
              return decorator
          
          def recover(self, error: Exception):
              strategy = self.recovery_strategies.get(type(error))
              if strategy:
                  return strategy(error)
              raise error
