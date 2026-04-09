#!/usr/bin/env python3
"""Simple HTTP server to serve the visualization page"""
import http.server
import socketserver
import os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        # Serve viz_final_v3.html as the index
        if self.path == '/' or self.path == '/index.html':
            self.path = '/viz_final_v3.html'
        return super().do_GET()
    
    def end_headers(self):
        # Add CORS and content type headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

print(f"Starting server on port {PORT}...")
print(f"Serving files from {DIRECTORY}")
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Server running at http://0.0.0.0:{PORT}")
    httpd.serve_forever()
