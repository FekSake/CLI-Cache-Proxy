from http.server import BaseHTTPRequestHandler
import sys


class ProxyRequestHandler(BaseHTTPRequestHandler):
    cache_manager = None
    proxy_client = None
    
    def do_GET(self):
        try:
            self.handleRequest()
        except Exception as e:
            print(f"Error handling request: {e}", file=sys.stderr)
            try:
                self.send_error(500, f"Internal Server Error: {e}")
            except:
                pass
    
    def handleRequest(self):
        path = self.path

        cached_response = self.cache_manager.get(path)

        if cached_response:
            self.sendResponseData(cached_response, 'HIT')
        else:
            response_data = self.proxy_client.forwardRequest(path)
            
            self.cache_manager.set(path, response_data)
            
            self.sendResponseData(response_data, 'MISS')
    
    def sendResponseData(self, response_data: dict, cache_status: str):
        try:
            self.send_response(response_data['status_code'])
            
            self.send_header('X-Cache', cache_status)
            
            body = response_data['body']
            if isinstance(body, str):
                body = body.encode('utf-8')
            
            self.send_header('Content-Length', len(body))
            skip_headers = ['server', 'date', 'content-length', 'transfer-encoding', 'connection', 'content-encoding']
            for header_name, header_value in response_data['headers'].items():
                if header_name.lower() not in skip_headers:
                    self.send_header(header_name, header_value)
            
            self.send_header('Connection', 'close')
            
            self.end_headers()
            
            self.wfile.write(body)
            self.wfile.flush()
        except Exception as e:
            print(f"Error sending response: {e}", file=sys.stderr)
