"""Response caching for AI client requests."""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class AICache:
    """Cache manager for AI responses."""
    
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        max_memory_entries: int = 100,
        default_ttl: int = 3600,  # 1 hour
        enable_disk_cache: bool = True,
    ):
        """Initialize AI cache.
        
        Args:
            cache_dir: Directory for disk cache (default: ~/.file_organizer/ai_cache)
            max_memory_entries: Maximum entries in memory cache
            default_ttl: Default time-to-live in seconds
            enable_disk_cache: Enable disk-based caching
        """
        self.memory_cache: Dict[str, Tuple[Any, float]] = {}
        self.max_memory_entries = max_memory_entries
        self.default_ttl = default_ttl
        self.enable_disk_cache = enable_disk_cache
        
        if cache_dir is None:
            cache_dir = Path.home() / ".file_organizer" / "ai_cache"
        self.cache_dir = Path(cache_dir)
        if self.enable_disk_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            "hits": 0,
            "misses": 0,
            "memory_hits": 0,
            "disk_hits": 0,
            "writes": 0,
            "evictions": 0,
        }
    
    def _hash_payload(self, payload: Dict[str, Any], provider: str) -> str:
        """Generate hash for payload and provider combination."""
        normalized = {
            "provider": provider,
            "payload": json.dumps(payload, sort_keys=True, default=str),
        }
        data = json.dumps(normalized, sort_keys=True).encode("utf-8")
        return hashlib.sha256(data).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get disk cache file path."""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(
        self,
        payload: Dict[str, Any],
        provider: str,
        ttl: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired."""
        cache_key = self._hash_payload(payload, provider)
        ttl = ttl or self.default_ttl
        now = time.time()
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            cached_data, expiry = self.memory_cache[cache_key]
            if now < expiry:
                self.stats["hits"] += 1
                self.stats["memory_hits"] += 1
                return cached_data
            else:
                del self.memory_cache[cache_key]
        
        # Check disk cache
        if self.enable_disk_cache:
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                try:
                    with cache_path.open("r", encoding="utf-8") as f:
                        cached = json.load(f)
                    cached_time = cached.get("timestamp", 0)
                    if now - cached_time < ttl:
                        result = cached.get("response")
                        if result:
                            self.memory_cache[cache_key] = (result, now + ttl)
                            if len(self.memory_cache) > self.max_memory_entries:
                                self._evict_oldest()
                            self.stats["hits"] += 1
                            self.stats["disk_hits"] += 1
                            return result
                    else:
                        cache_path.unlink()
                except Exception:
                    try:
                        cache_path.unlink()
                    except Exception:
                        pass
        
        self.stats["misses"] += 1
        return None
    
    def set(
        self,
        payload: Dict[str, Any],
        provider: str,
        response: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> None:
        """Cache a response."""
        cache_key = self._hash_payload(payload, provider)
        ttl = ttl or self.default_ttl
        now = time.time()
        expiry = now + ttl
        
        self.memory_cache[cache_key] = (response, expiry)
        
        if len(self.memory_cache) > self.max_memory_entries:
            self._evict_oldest()
        
        if self.enable_disk_cache:
            cache_path = self._get_cache_path(cache_key)
            try:
                cache_data = {
                    "timestamp": now,
                    "provider": provider,
                    "response": response,
                }
                with cache_path.open("w", encoding="utf-8") as f:
                    json.dump(cache_data, f, default=str)
                self.stats["writes"] += 1
            except Exception:
                pass
    
    def _evict_oldest(self) -> None:
        """Evict oldest entry from memory cache."""
        if not self.memory_cache:
            return
        oldest_key = min(self.memory_cache.keys(), key=lambda k: self.memory_cache[k][1])
        del self.memory_cache[oldest_key]
        self.stats["evictions"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "memory_entries": len(self.memory_cache),
            "disk_entries": len(list(self.cache_dir.glob("*.json"))) if self.enable_disk_cache else 0,
        }


# Global cache instance
_global_cache: Optional[AICache] = None


def get_cache() -> AICache:
    """Get or create global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = AICache()
    return _global_cache

