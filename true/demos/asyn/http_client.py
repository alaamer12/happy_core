"""Example of using Asyn with httpx for async HTTP requests."""

import asyncio
import logging
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional
import httpx
from true.asyn import Asyn, TaskState, TaskPriority

# Create separate loggers
diagnostic_logger = logging.getLogger('diagnostic')
progress_logger = logging.getLogger('progress')

@dataclass
class RequestResult:
    """Result of an HTTP request."""
    url: str
    status_code: int
    success: bool
    content_length: int
    elapsed: float
    error: Optional[str] = None

class AsyncHttpClient:
    """Make concurrent HTTP requests using httpx."""
    
    def __init__(self, concurrency: int = 5):
        self.concurrency = concurrency
        self.results: List[RequestResult] = []
        self._running = True
        
        # Common request headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def make_request(self, client: httpx.AsyncClient, url: str) -> RequestResult:
        """Make a single HTTP request."""
        try:
            start_time = asyncio.get_event_loop().time()
            async with client.stream('GET', url) as response:
                # Read and discard response content
                async for _ in response.aiter_bytes():
                    pass
                
                elapsed = asyncio.get_event_loop().time() - start_time
                result = RequestResult(
                    url=url,
                    status_code=response.status_code,
                    success=response.is_success,
                    content_length=int(response.headers.get('content-length', 0)),
                    elapsed=elapsed
                )
                
                progress_logger.info(
                    f"Request to {url} completed: "
                    f"status={result.status_code}, "
                    f"size={result.content_length} bytes, "
                    f"time={result.elapsed:.2f}s"
                )
                return result
                
        except Exception as e:
            diagnostic_logger.error(f"Error requesting {url}: {e}")
            return RequestResult(
                url=url,
                status_code=0,
                success=False,
                content_length=0,
                elapsed=0,
                error=str(e)
            )

    async def process_batch(self, urls: List[str], semaphore: asyncio.Semaphore):
        """Process a batch of URLs with concurrency limit."""
        async with httpx.AsyncClient(
            headers=self.headers,
            follow_redirects=True,
            timeout=30.0
        ) as client:
            for url in urls:
                async with semaphore:
                    result = await self.make_request(client, url)
                    self.results.append(result)

    async def start(self, urls: List[str]):
        """Start making HTTP requests."""
        print("\n=== Starting HTTP Client ===")
        print(f"URLs to Process: {len(urls)}")
        print(f"Max Concurrency: {self.concurrency}\n")
        
        try:
            async with Asyn(name="http_client") as manager:
                # Create semaphore for concurrency control
                semaphore = asyncio.Semaphore(self.concurrency)
                
                # Split URLs into batches
                batch_size = 10
                batches = [
                    urls[i:i + batch_size]
                    for i in range(0, len(urls), batch_size)
                ]
                
                # Process batches
                batch_tasks = []
                for i, batch in enumerate(batches):
                    batch_task = await manager.create_task(
                        self.process_batch(batch, semaphore),
                        name=f"batch_{i}"
                    )
                    batch_tasks.append(batch_task)
                
                # Wait for all batches to complete
                await manager.wait_for_children()
                
                # Print summary
                print("\n=== Request Summary ===\n")
                
                # Group by status code
                status_groups: Dict[int, List[RequestResult]] = {}
                total_time = 0
                total_bytes = 0
                
                for result in self.results:
                    status_groups.setdefault(result.status_code, []).append(result)
                    if result.success:
                        total_time += result.elapsed
                        total_bytes += result.content_length
                
                # Print status code groups
                for status_code, results in sorted(status_groups.items()):
                    if status_code == 0:
                        print(f"Failed Requests: {len(results)}")
                        for result in results:
                            print(f"  {result.url}: {result.error}")
                    else:
                        print(f"Status {status_code}: {len(results)} requests")
                
                print(f"\nTotal Requests: {len(self.results)}")
                print(f"Successful: {sum(1 for r in self.results if r.success)}")
                print(f"Failed: {sum(1 for r in self.results if not r.success)}")
                print(f"Total Time: {total_time:.2f}s")
                print(f"Total Data: {total_bytes / 1024:.1f} KB")
                
        except Exception as e:
            diagnostic_logger.error(f"Error in HTTP client: {e}")
            raise

async def main():
    """Run the HTTP client example."""
    # Test URLs
    urls = [
        'https://www.python.org',
        'https://docs.python.org',
        'https://pypi.org',
        'https://github.com/python',
        'https://www.python.org/downloads/',
        'https://docs.python.org/3/',
        'https://www.python.org/community/',
        'https://www.python.org/about/',
        'https://www.python.org/success-stories/',
        'https://www.python.org/blogs/',
    ]
    
    client = AsyncHttpClient(concurrency=3)
    await client.start(urls)

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
    
    # Run the HTTP client
    asyncio.run(main())
