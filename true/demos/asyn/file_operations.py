"""Example of using Asyn with aiopath and aiofiles for async file operations."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict
from aiopath import AsyncPath
import aiofiles
from true.asyn import Asyn, TaskState, TaskPriority

# Create separate loggers
diagnostic_logger = logging.getLogger('diagnostic')
progress_logger = logging.getLogger('progress')

class FileProcessor:
    """Process files asynchronously using aiopath and aiofiles."""
    
    def __init__(self, base_dir: str):
        self.base_dir = AsyncPath(base_dir)
        self.file_stats: Dict[str, Dict] = {}
        self._running = True

    async def scan_directory(self, directory: AsyncPath) -> List[AsyncPath]:
        """Scan directory for files recursively."""
        files = []
        try:
            async for entry in directory.iterdir():
                is_file = await entry.is_file()
                if is_file:
                    files.append(entry)
                else:
                    is_dir = await entry.is_dir()
                    if is_dir:
                        subfiles = await self.scan_directory(entry)
                        files.extend(subfiles)
        except Exception as e:
            diagnostic_logger.error(f"Error scanning {directory}: {e}")
        return files

    async def process_file(self, file_path: AsyncPath) -> Dict:
        """Process a single file."""
        try:
            stats = {
                'size': (await file_path.stat()).st_size,
                'lines': 0,
                'words': 0,
                'chars': 0
            }
            
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                stats['chars'] = len(content)
                lines = content.splitlines()
                stats['lines'] = len(lines)
                stats['words'] = sum(len(line.split()) for line in lines)
            
            progress_logger.info(
                f"Processed {file_path.name}: "
                f"{stats['lines']} lines, {stats['words']} words"
            )
            return stats
            
        except Exception as e:
            diagnostic_logger.error(f"Error processing {file_path}: {e}")
            return None

    async def backup_file(self, file_path: AsyncPath) -> bool:
        """Create a backup copy of a file."""
        try:
            backup_path = AsyncPath(str(file_path) + '.bak')
            async with aiofiles.open(file_path, mode='rb') as src:
                content = await src.read()
                async with aiofiles.open(backup_path, mode='wb') as dst:
                    await dst.write(content)
            
            progress_logger.info(f"Created backup: {backup_path.name}")
            return True
            
        except Exception as e:
            diagnostic_logger.error(f"Error backing up {file_path}: {e}")
            return False

    async def start(self):
        """Start processing files."""
        print(f"\n=== Starting File Processor ===")
        print(f"Base Directory: {self.base_dir}\n")
        
        try:
            async with Asyn(name="file_processor") as manager:
                # Scan for files
                progress_logger.info("Scanning directory...")
                files = await self.scan_directory(self.base_dir)
                progress_logger.info(f"Found {len(files)} files")
                
                # Process files
                process_tasks = []
                backup_tasks = []
                
                for file in files:
                    # Create process task
                    process_task = await manager.create_task(
                        self.process_file(file),
                        name=f"process_{file.name}"
                    )
                    process_tasks.append(process_task)
                    
                    # Create backup task
                    backup_task = await manager.create_task(
                        self.backup_file(file),
                        name=f"backup_{file.name}"
                    )
                    backup_tasks.append(backup_task)
                
                # Wait for all tasks to complete
                await manager.wait_for_children()
                
                # Print summary
                print("\n=== Processing Summary ===\n")
                total_lines = 0
                total_words = 0
                total_size = 0
                
                for file in files:
                    try:
                        stats = await self.process_file(file)
                        if stats:
                            print(f"File: {file.name}")
                            print(f"  Lines: {stats['lines']}")
                            print(f"  Words: {stats['words']}")
                            print(f"  Size: {stats['size']} bytes")
                            print()
                            
                            total_lines += stats['lines']
                            total_words += stats['words']
                            total_size += stats['size']
                    except Exception as e:
                        diagnostic_logger.error(f"Error getting stats for {file}: {e}")
                
                print("=== Totals ===")
                print(f"Files Processed: {len(files)}")
                print(f"Total Lines: {total_lines}")
                print(f"Total Words: {total_words}")
                print(f"Total Size: {total_size} bytes")
                
        except Exception as e:
            diagnostic_logger.error(f"Error in file processor: {e}")
            raise

async def main():
    """Run the file operations example."""
    # Use the current directory as base
    base_dir = Path(__file__).parent
    processor = FileProcessor(str(base_dir))
    await processor.start()

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
    
    # Run the file processor
    asyncio.run(main())
