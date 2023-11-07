# always_serve_index.py
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

class CustomHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Try to find the requested file in the 'dist' directory
        potential_path = os.path.join(os.getcwd(), 'dist', path.lstrip('/'))

        # If the file exists, serve it. Otherwise, default to index.html
        if os.path.exists(potential_path) and not os.path.isdir(potential_path):
            return potential_path
        else:
            return os.path.join(os.getcwd(), 'dist', 'index.html')

if __name__ == '__main__':
    httpd = HTTPServer(('0.0.0.0', 8000), CustomHandler)
    httpd.serve_forever()

