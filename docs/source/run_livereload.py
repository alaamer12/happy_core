from livereload import Server
import os
import sys
import subprocess

def build_docs():
    docs_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_dir = os.path.join(docs_dir, 'source')
    build_dir = os.path.join(docs_dir, 'build', 'html')
    
    try:
        subprocess.run([
            'sphinx-build',
            '-b', 'html',
            '-q',  # quiet mode
            source_dir,
            build_dir
        ], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

if __name__ == '__main__':
    docs_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_dir = os.path.join(docs_dir, 'source')
    build_dir = os.path.join(docs_dir, 'build', 'html')
    
    os.makedirs(build_dir, exist_ok=True)
    build_docs()
    
    server = Server()
    
    # Watch all relevant files
    patterns = ['*.rst', '*.css', '*.md', '*.py', '_static/*', '_templates/*', 'examples/*', 'modules/*', 'releases/*', 'changelogs/*']
    for pattern in patterns:
        server.watch(os.path.join(source_dir, pattern), build_docs)
    
    print("\nDocumentation server starting...")
    print(f"→ URL: http://127.0.0.1:5500")
    print("Press Ctrl+C to stop\n")
    
    try:
        server.serve(
            root=build_dir,
            port=5500,
            host='127.0.0.1',
            restart_delay=0,  # Immediate refresh
            open_url_delay=None,  # Don't auto-open browser
            live_css=True,  # Enable live CSS reloading
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)