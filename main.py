import argparse
import sys
from urllib.parse import urlparse


def parseArguments():
    parser = argparse.ArgumentParser(
        description='Caching Proxy Server - Cache HTTP responses from an origin server',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--port',
        type=int,
        help='Port number for the proxy server (1-65535)'
    )
    
    parser.add_argument(
        '--origin',
        type=str,
        help='Origin server URL (e.g., http://example.com)'
    )
    
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear the cache and exit'
    )
    
    parser.add_argument(
        '--cache-ttl',
        type=int,
        help='Cache time-to-live in seconds (optional). Cached entries will expire after this duration.'
    )
    
    args = parser.parse_args()
    
    if args.clear_cache:
        return args
    
    if args.port is None or args.origin is None:
        parser.error('--port and --origin are required when not using --clear-cache')
    
    if args.port < 1 or args.port > 65535:
        print(f'Error: Port number must be between 1 and 65535, got {args.port}', file=sys.stderr)
        sys.exit(1)
    
    try:
        parsed_url = urlparse(args.origin)
        if not parsed_url.scheme or not parsed_url.netloc:
            print(f'Error: Invalid origin URL format: {args.origin}', file=sys.stderr)
            print('Origin URL must include scheme and host (e.g., http://example.com)', file=sys.stderr)
            sys.exit(1)
        if parsed_url.scheme not in ['http', 'https']:
            print(f'Error: Origin URL must use http or https scheme, got {parsed_url.scheme}', file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f'Error: Invalid origin URL: {args.origin} - {e}', file=sys.stderr)
        sys.exit(1)
    
    return args


def main():
    try:
        args = parseArguments()
        
        if args.clear_cache:
            from cache_manager import CacheManager
            
            try:
                cache_manager = CacheManager()
                cache_manager.clear()
                
                print('Cache cleared successfully')
                sys.exit(0)
            except Exception as e:
                print(f'Error: Failed to clear cache - {e}', file=sys.stderr)
                sys.exit(1)
        
        from server import startServer
        
        try:
            startServer(args.port, args.origin, args.cache_ttl)
        except ValueError as e:
            print(f'Error: {e}', file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f'Error: Failed to start server - {e}', file=sys.stderr)
            sys.exit(1)
    
    except KeyboardInterrupt:
        print('\nOperation cancelled by user')
        sys.exit(0)
    except SystemExit:
        raise
    except Exception as e:
        print(f'Error: An unexpected error occurred - {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
