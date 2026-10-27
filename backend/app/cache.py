import time
from typing import Optional, Dict, Tuple
from .schemas.contract import AnalyzeResponse
from .config import settings

class AnalysisCache:
    """
    In-memory TTL cache with a maximum capacity limit and LRU-style eviction.
    Keyed by 'owner/repo@branch-or-sha'.
    """

    def __init__(self, ttl_seconds: Optional[int] = None, max_size: int = 50):
        self.ttl = ttl_seconds if ttl_seconds is not None else settings.CACHE_TTL_SECONDS
        self.max_size = max_size
        # key -> (AnalyzeResponse, expiry_timestamp, access_timestamp)
        self._store: Dict[str, Tuple[AnalyzeResponse, float, float]] = {}

    def get(self, key: str) -> Optional[AnalyzeResponse]:
        now = time.time()
        if key in self._store:
            data, expires_at, _ = self._store[key]
            if now < expires_at:
                # Update last accessed time
                self._store[key] = (data, expires_at, now)
                return data
            else:
                # Expired
                del self._store[key]
        return None

    def set(self, key: str, value: AnalyzeResponse):
        now = time.time()
        # Evict oldest accessed item if at max capacity
        if len(self._store) >= self.max_size and key not in self._store:
            oldest_key = min(self._store.keys(), key=lambda k: self._store[k][2])
            del self._store[oldest_key]

        expires_at = now + self.ttl
        self._store[key] = (value, expires_at, now)

    def clear(self):
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)

# Global cache instance
analysis_cache = AnalysisCache()
