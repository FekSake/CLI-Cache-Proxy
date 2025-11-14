from http.server import HTTPServer
import signal
import sys
from cache_manager import CacheManager
from proxy_client import ProxyClient
from proxy_handler import ProxyRequestHandler


def startServer(port: int, origin_url: str, cache_ttl: int = None) -> None:
    cache_manager = CacheManager(ttl=cache_ttl)
    proxy_client = ProxyClient(origin_url)
    
    ProxyRequestHandler.cache_manager = cache_manager
    ProxyRequestHandler.proxy_client = proxy_client
    
    try:
        class StrictHTTPServer(HTTPServer):
            allow_reuse_address = False
        
        server = StrictHTTPServer(('localhost', port), ProxyRequestHandler)
    except OSError as e:
        error_msg = str(e).lower()
        if 'address already in use' in error_msg or e.errno in [98, 10048]:
            print(f'Error: Port {port} is already in use', file=sys.stderr)
            sys.exit(1)
        elif 'permission denied' in error_msg or e.errno in [13, 10013]:
            print(f'Error: Permission denied to bind to port {port}', file=sys.stderr)
            sys.exit(1)
        else:
            print(f'Error: Could not start server on port {port}: {e}', file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f'Error: Failed to start server: {e}', file=sys.stderr)
        sys.exit(1)
    
    def shutdownHandler(signum, frame):
        print('\nShutting down server...')
        cache_manager.saveCache()
        print('Cache saved successfully')
        server.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, shutdownHandler)
    signal.signal(signal.SIGTERM, shutdownHandler)
    
    print(f'Caching proxy server started on port {port}')
    print(f'Forwarding requests to: {origin_url}')
    if cache_ttl:
        print(f'Cache TTL: {cache_ttl} seconds')
    print('Press Ctrl+C to stop the server')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
        cache_manager.saveCache()
        print('Cache saved successfully')
        sys.exit(0)
