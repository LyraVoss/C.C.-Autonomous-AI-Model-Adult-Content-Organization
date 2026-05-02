from functools import lru_cache
from typing import Dict, List, Optional
import asyncio
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime
from .models import DigitalCreator, ContentPost, ContentType

class PerformanceOptimizer:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour

    @lru_cache(maxsize=1000)
    def cached_content_generation(self, creator_id: str, theme: str, content_type: str) -> Optional[ContentPost]:
        """Cache content generation results"""
        cache_key = f"{creator_id}_{theme}_{content_type}"
        if cache_key in self.cache:
            cached_time, cached_content = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_content
            else:
                del self.cache[cache_key]
        return None

    def set_cached_content(self, creator_id: str, theme: str, content_type: str, content: ContentPost):
        """Store content in cache"""
        cache_key = f"{creator_id}_{theme}_{content_type}"
        self.cache[cache_key] = (time.time(), content)

    async def parallel_content_generation(self, creator: DigitalCreator, themes: List[str]) -> List[ContentPost]:
        """Generate multiple content pieces in parallel"""
        tasks = []
        for theme in themes:
            for content_type in [ContentType.TEXT, ContentType.IMAGE]:
                task = self._generate_single_content_async(creator, theme, content_type)
                tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]

    async def _generate_single_content_async(self, creator: DigitalCreator, theme: str, content_type: ContentType) -> ContentPost:
        """Generate single content piece asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._generate_content_sync,
            creator, theme, content_type
        )

    def _generate_content_sync(self, creator: DigitalCreator, theme: str, content_type: ContentType) -> ContentPost:
        """Synchronous content generation (placeholder)"""
        # This would call the actual AI generation
        return ContentPost(
            id=f"{creator.id}_{theme}_{content_type.value}_{time.time()}",
            creator_id=creator.id,
            type=content_type,
            title=f"{creator.name}'s {theme}",
            description=f"AI-generated {content_type.value} content",
            created_at=datetime.now()
        )

    def optimize_stream_performance(self, stream_data: Dict) -> Dict:
        """Optimize streaming data for performance"""
        # Compress chat messages
        if 'chat_messages' in stream_data:
            # Keep only recent messages
            stream_data['chat_messages'] = stream_data['chat_messages'][-50:]

        # Aggregate viewer stats
        if 'viewers' in stream_data:
            stream_data['viewer_count'] = len(stream_data['viewers'])
            # Don't send full viewer list for performance
            del stream_data['viewers']

        return stream_data

    def batch_database_operations(self, operations: List[Dict]) -> List[Dict]:
        """Batch database operations for efficiency"""
        # Group operations by type
        inserts = [op for op in operations if op['type'] == 'insert']
        updates = [op for op in operations if op['type'] == 'update']
        deletes = [op for op in operations if op['type'] == 'delete']

        results = []

        # Execute in batches
        for batch in [inserts, updates, deletes]:
            if batch:
                # Execute batch operation
                results.extend(self._execute_batch(batch))

        return results

    def _execute_batch(self, batch: List[Dict]) -> List[Dict]:
        """Execute a batch of operations"""
        # Placeholder for actual batch execution
        return [{"status": "success", "operation": op} for op in batch]

    def memory_efficient_processing(self, large_dataset: List[Dict], batch_size: int = 100) -> List[Dict]:
        """Process large datasets in memory-efficient batches"""
        results = []
        for i in range(0, len(large_dataset), batch_size):
            batch = large_dataset[i:i + batch_size]
            processed_batch = self._process_batch(batch)
            results.extend(processed_batch)
            # Force garbage collection if needed
            if len(results) % 1000 == 0:
                import gc
                gc.collect()
        return results

    def _process_batch(self, batch: List[Dict]) -> List[Dict]:
        """Process a single batch"""
        # Placeholder processing
        return batch

    def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (timestamp, _) in self.cache.items()
            if current_time - timestamp > self.cache_ttl
        ]
        for key in expired_keys:
            del self.cache[key]

    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics"""
        return {
            "cache_size": len(self.cache),
            "active_threads": self.executor._threads,
            "memory_usage": "placeholder",  # Would use psutil
            "uptime": time.time()  # Placeholder
        }