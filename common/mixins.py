from django.core.cache import cache


class CacheMixin:
    def get_set_cache(self, query, cache_name, cache_time):
        cached_data = cache.get(cache_name)

        if not cached_data:
            cached_data = query
            cache.set(cache_name, cached_data, cache_time)

        return cached_data


