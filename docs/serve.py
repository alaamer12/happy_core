import http.server
import socketserver
import os
from pathlib import Path

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Convert the path to a file path
        path = self.translate_path(self.path)
        
        # If the file doesn't exist, serve the 404 page
        if not os.path.exists(path):
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Read and serve the 404.html file
            try:
                with open('404.html', 'rb') as f:
                    content = f.read()
                    # Replace absolute paths with relative paths
                    content = content.replace(b'/_static/', b'_static/')
                    content = content.replace(b'/_images/', b'_images/')
                    self.wfile.write(content)
            except Exception as e:
                print(f"Error serving 404 page: {e}")
                self.wfile.write(b'404 - Page Not Found')
        else:
            # Serve the requested file
            super().do_GET()

PORT = 8000

# Change to the build/html directory
os.chdir(str(Path(__file__).parent / 'build' / 'html'))

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving documentation at http://localhost:{PORT}")
    print(f"Try accessing http://localhost:{PORT}/non-existent-page to see the 404 page")
    httpd.serve_forever()
