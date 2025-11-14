import json
import os
from typing import Optional


class CacheManager:
    
    def __init__(self, cache_file='cache.json'):
        self.cache_file = cache_file
        self.cache = {}
        self.loadCache()
    
    def get(self, key: str) -> Optional[dict]:
        return self.cache.get(key)
    
    def set(self, key: str, response_data: dict) -> None:
        self.cache[key] = response_data
        self.saveCache()
    
    def clear(self) -> None:
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
    
    def loadCache(self) -> None:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load cache file: {e}. Starting with empty cache.")
                self.cache = {}
        else:
            self.cache = {}
    
    def saveCache(self) -> None:
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save cache file: {e}")
