cache = {}

def cache_battery_status(bid, status):
    cache[bid] = status

def get_cached_battery_status(bid):
    return cache.get(bid)
