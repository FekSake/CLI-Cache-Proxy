import requests
from urllib.parse import urlparse, urljoin


class ProxyClient:
    
    def __init__(self, origin_url):
        parsed_url = urlparse(origin_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Invalid origin URL format: {origin_url}")
        if parsed_url.scheme not in ['http', 'https']:
            raise ValueError(f"Origin URL must use http or https scheme, got {parsed_url.scheme}")
        
        self.origin_url = origin_url.rstrip('/')
    
    def forwardRequest(self, path: str, method: str = 'GET', headers: dict = None) -> dict:
        full_url = urljoin(self.origin_url + '/', path.lstrip('/'))
        
        try:
            response = requests.request(
                method=method,
                url=full_url,
                headers=headers,
                timeout=30
            )
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': response.text
            }
        
        except requests.exceptions.ConnectionError as e:
            return {
                'status_code': 502,
                'headers': {'Content-Type': 'text/plain'},
                'body': f'Bad Gateway: Could not connect to origin server - {str(e)}'
            }
        
        except requests.exceptions.Timeout as e:
            return {
                'status_code': 504,
                'headers': {'Content-Type': 'text/plain'},
                'body': f'Gateway Timeout: Origin server did not respond in time - {str(e)}'
            }
        
        except requests.exceptions.RequestException as e:
            return {
                'status_code': 502,
                'headers': {'Content-Type': 'text/plain'},
                'body': f'Bad Gateway: Error communicating with origin server - {str(e)}'
            }
