# Caching Proxy Server

A lightweight HTTP caching proxy server that forwards requests to an origin server and caches responses to improve performance and reduce load on the origin server.

This is a roadmap.sh project https://roadmap.sh/projects/caching-server

## Features

- **HTTP Proxy**: Forwards requests to a configurable origin server
- **Response Caching**: Caches responses to reduce redundant requests
- **Cache Headers**: Adds `X-Cache` header to indicate cache hits/misses
- **Persistent Cache**: Saves cache to disk for persistence across restarts
- **Cache TTL**: Optional time-to-live for automatic cache expiration
- **Cache Management**: Clear cache on demand
- **Error Handling**: Graceful handling of connection errors, timeouts, and port conflicts

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CLI-Cache-Proxy
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Start the Proxy Server

```bash
python main.py --port <port> --origin <origin-url>
```

**Example:**
```bash
python main.py --port 3000 --origin http://dummyjson.com
```

### Start with Cache TTL

Enable automatic cache expiration by setting a time-to-live in seconds:

```bash
python main.py --port 3000 --origin http://dummyjson.com --cache-ttl 300
```

This will automatically expire cached entries after 300 seconds (5 minutes). Each entry expires independently based on when it was cached.

### Clear the Cache

```bash
python main.py --clear-cache
```

## Command-Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--port` | Yes* | Port number for the proxy server (1-65535) |
| `--origin` | Yes* | Origin server URL (e.g., http://example.com) |
| `--cache-ttl` | No | Cache time-to-live in seconds. Entries expire after this duration |
| `--clear-cache` | No | Clear the cache and exit |

*Required when not using `--clear-cache`

## How It Works

1. **Request Flow**:
   - Client sends request to proxy server
   - Proxy checks if response is cached
   - If cached (HIT): Returns cached response
   - If not cached (MISS): Forwards request to origin server, caches response, returns to client

2. **Cache Headers**:
   - `X-Cache: HIT` - Response served from cache
   - `X-Cache: MISS` - Response fetched from origin server

3. **Cache Expiration** (when TTL is enabled):
   - Each cached entry stores a timestamp
   - Entries are checked for expiration on access
   - Background cleanup thread removes expired entries every 10 seconds

## Examples

### Basic Usage

```bash
# Start proxy server on port 3000
python main.py --port 3000 --origin http://dummyjson.com

# Make requests through the proxy
curl http://localhost:3000/products/1
# X-Cache: MISS (first request)

curl http://localhost:3000/products/1
# X-Cache: HIT (cached response)
```

### With Cache TTL

```bash
# Start with 60-second cache expiration
python main.py --port 3000 --origin http://dummyjson.com --cache-ttl 60

# First request at time 0s
curl http://localhost:3000/products/1
# X-Cache: MISS

# Request at time 30s (within TTL)
curl http://localhost:3000/products/1
# X-Cache: HIT

# Request at time 70s (after TTL expired)
curl http://localhost:3000/products/1
# X-Cache: MISS (cache expired, fetches fresh data)
```

### Cache Management

```bash
# Clear all cached entries
python main.py --clear-cache
# Output: Cache cleared successfully
```

## Architecture

The project consists of the following components:

- **main.py**: CLI entry point and argument parsing
- **server.py**: HTTP server lifecycle management
- **proxy_handler.py**: Request handling and cache coordination
- **proxy_client.py**: Origin server communication
- **cache_manager.py**: Cache storage, retrieval, and expiration logic

## Error Handling

The proxy server handles various error scenarios:

- **Port Conflicts**: Detects when the specified port is already in use
- **Permission Errors**: Handles permission denied errors for privileged ports
- **Connection Errors**: Returns 502 Bad Gateway when origin server is unreachable
- **Timeout Errors**: Returns 504 Gateway Timeout when origin server doesn't respond
- **Invalid URLs**: Validates origin URL format before starting

## Cache Storage

- Cache is stored in `cache.json` in the current directory
- Cache persists across server restarts (when TTL is not enabled)
- When TTL is enabled, cache is not loaded from disk on startup
- Cache is automatically saved when entries are added or removed

## Requirements

- Python 3.6+
