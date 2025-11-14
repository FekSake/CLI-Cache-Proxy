import json
import os
import time
import threading
from typing import Optional


class CacheManager:
    
    def __init__(self, cache_file='cache.json', ttl=None):
        self.cache_file = cache_file
        self.cache = {}
        self.ttl = ttl
        self.lock = threading.Lock()
        self.loadCache()
        
        if self.ttl:
            self.cleanupThread = threading.Thread(target=self._cleanupExpiredEntries, daemon=True)
            self.cleanupThread.start()
    
    def get(self, key: str) -> Optional[dict]:
        with self.lock:
            entry = self.cache.get(key)
            if entry is None:
                return None
            
            if self.ttl:
                timestamp = entry.get('timestamp')
                if timestamp and (time.time() - timestamp) > self.ttl:
                    del self.cache[key]
                    return None
                return entry.get('data')
            
            return entry
    
    def set(self, key: str, response_data: dict) -> None:
        with self.lock:
            if self.ttl:
                self.cache[key] = {
                    'data': response_data,
                    'timestamp': time.time()
                }
            else:
                self.cache[key] = response_data
        self.saveCache()
    
    def _cleanupExpiredEntries(self):
        while True:
            time.sleep(10)
            if self.ttl:
                with self.lock:
                    current_time = time.time()
                    expired_keys = [
                        key for key, entry in self.cache.items()
                        if isinstance(entry, dict) and 'timestamp' in entry and (current_time - entry['timestamp']) > self.ttl
                    ]
                    if expired_keys:
                        for key in expired_keys:
                            del self.cache[key]
                self.saveCache()
    
    def clear(self) -> None:
        with self.lock:
            self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
    
    def loadCache(self) -> None:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    loaded_cache = json.load(f)
                    
                    if self.ttl:
                        self.cache = {}
                    else:
                        self.cache = loaded_cache
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load cache file: {e}. Starting with empty cache.")
                self.cache = {}
        else:
            self.cache = {}
    
    def saveCache(self) -> None:
        try:
            with self.lock:
                cache_copy = self.cache.copy()
            with open(self.cache_file, 'w') as f:
                json.dump(cache_copy, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save cache file: {e}")
