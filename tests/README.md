# Cache System Test Suite

This directory contains a comprehensive test suite for the caching system, including unit tests, integration tests, and performance benchmarks.

## Test Files

1. **test_cache_basic.py**
   - Basic operations (set/get)
   - TTL functionality
   - Size limits
   - Error cases
   - Basic metrics

2. **test_cache_advanced.py**
   - Compression features
   - Caching policies (LRU, LFU, Hybrid)
   - Memory management
   - Advanced features

3. **test_cache_async.py**
   - Async operations
   - Batch processing
   - Concurrent access
   - Performance comparisons

4. **test_cache_distributed.py**
   - Redis integration
   - Sharding
   - Fault tolerance
   - Distributed operations

## Running Tests

### Basic Usage
```bash
# Run all tests
pytest

# Run specific test file
pytest test_cache_basic.py

# Run tests by category
pytest -m basic
pytest -m advanced
pytest -m async_
pytest -m distributed
```

### Benchmarks
```bash
# Run all benchmarks
pytest --benchmark-only

# Run specific benchmark
pytest test_cache_basic.py --benchmark-only

# Generate benchmark report
pytest --benchmark-only --benchmark-json output.json
```

### Test Categories
- `basic`: Basic functionality tests
- `advanced`: Advanced feature tests
- `async_`: Asynchronous operation tests
- `distributed`: Distributed caching tests
- `benchmark`: Performance benchmarks
- `slow`: Time-consuming tests

## Requirements

- pytest
- pytest-asyncio
- pytest-benchmark
- redis (for distributed tests)

## Configuration

The test suite uses the following configuration:
- Custom test categories and markers
- Benchmark configuration in conftest.py
- Shared fixtures for test data
- Integration test markers

## Performance Testing

The benchmark tests measure:
- Operation latency
- Memory usage
- Compression ratios
- Async vs sync performance
- Local vs distributed performance

Results are available in JSON format for analysis.
