from django.core.cache import cache


class ContactRateLimitService:
    @staticmethod
    def get_cache_key(ip_address: str) -> str:
        return f"contact-rate-limit:{ip_address or 'unknown'}"

    @classmethod
    def check_request_allowed(cls, ip_address: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        cache_key = cls.get_cache_key(ip_address)
        current_value = cache.get(cache_key)

        if current_value is None:
            cache.set(cache_key, 1, timeout=window_seconds)
            return True, 0

        if current_value >= limit:
            return False, window_seconds

        try:
            cache.incr(cache_key)
        except ValueError:
            cache.set(cache_key, current_value + 1, timeout=window_seconds)

        return True, 0
