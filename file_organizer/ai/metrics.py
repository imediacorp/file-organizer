"""Performance metrics and telemetry for AI client usage."""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AIMetric:
    """Single AI request metric."""
    provider: str
    timestamp: float
    duration_ms: float
    success: bool
    error: Optional[str] = None
    cached: bool = False
    payload_size: int = 0
    response_size: int = 0


@dataclass
class ProviderStats:
    """Statistics for a specific provider."""
    provider: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    total_payload_size: int = 0
    total_response_size: int = 0
    errors: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_request_time: Optional[float] = None


class AIMetricsCollector:
    """Collector for AI performance metrics."""
    
    def __init__(self, max_metrics: int = 1000):
        """Initialize metrics collector."""
        self.metrics: List[AIMetric] = []
        self.max_metrics = max_metrics
        self.provider_stats: Dict[str, ProviderStats] = {}
    
    def record(
        self,
        provider: str,
        duration_ms: float,
        success: bool,
        cached: bool = False,
        error: Optional[str] = None,
        payload_size: int = 0,
        response_size: int = 0,
    ) -> None:
        """Record a metric."""
        metric = AIMetric(
            provider=provider,
            timestamp=time.time(),
            duration_ms=duration_ms,
            success=success,
            error=error,
            cached=cached,
            payload_size=payload_size,
            response_size=response_size,
        )
        
        self.metrics.append(metric)
        
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
        
        if provider not in self.provider_stats:
            self.provider_stats[provider] = ProviderStats(provider=provider)
        
        stats = self.provider_stats[provider]
        stats.total_requests += 1
        stats.last_request_time = metric.timestamp
        
        if success:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1
            if error:
                stats.errors[error] += 1
        
        if cached:
            stats.cache_hits += 1
        else:
            stats.cache_misses += 1
        
        stats.total_duration_ms += duration_ms
        stats.avg_duration_ms = stats.total_duration_ms / stats.total_requests
        
        if duration_ms < stats.min_duration_ms:
            stats.min_duration_ms = duration_ms
        if duration_ms > stats.max_duration_ms:
            stats.max_duration_ms = duration_ms
        
        stats.total_payload_size += payload_size
        stats.total_response_size += response_size
    
    def get_provider_stats(self, provider: str) -> Optional[ProviderStats]:
        """Get statistics for a specific provider."""
        return self.provider_stats.get(provider)
    
    def get_all_stats(self) -> Dict[str, ProviderStats]:
        """Get statistics for all providers."""
        return dict(self.provider_stats)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        total_requests = len(self.metrics)
        if total_requests == 0:
            return {
                "total_requests": 0,
                "providers": {},
                "overall_success_rate": 0.0,
                "overall_avg_duration_ms": 0.0,
            }
        
        successful = sum(1 for m in self.metrics if m.success)
        cached = sum(1 for m in self.metrics if m.cached)
        total_duration = sum(m.duration_ms for m in self.metrics)
        
        provider_summaries = {}
        for provider, stats in self.provider_stats.items():
            provider_summaries[provider] = {
                "total_requests": stats.total_requests,
                "success_rate": (stats.successful_requests / stats.total_requests * 100) if stats.total_requests > 0 else 0.0,
                "avg_duration_ms": round(stats.avg_duration_ms, 2),
                "min_duration_ms": round(stats.min_duration_ms, 2) if stats.min_duration_ms != float("inf") else 0.0,
                "max_duration_ms": round(stats.max_duration_ms, 2),
                "cache_hit_rate": (stats.cache_hits / (stats.cache_hits + stats.cache_misses) * 100) if (stats.cache_hits + stats.cache_misses) > 0 else 0.0,
                "errors": dict(stats.errors),
            }
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful,
            "failed_requests": total_requests - successful,
            "overall_success_rate": round(successful / total_requests * 100, 2),
            "overall_avg_duration_ms": round(total_duration / total_requests, 2),
            "cache_hits": cached,
            "cache_hit_rate": round(cached / total_requests * 100, 2),
            "providers": provider_summaries,
        }


# Global metrics collector
_global_collector: Optional[AIMetricsCollector] = None


def get_metrics_collector() -> AIMetricsCollector:
    """Get or create global metrics collector."""
    global _global_collector
    if _global_collector is None:
        _global_collector = AIMetricsCollector()
    return _global_collector

