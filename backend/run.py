import os
import sys
import uvicorn

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # fallback to 8000 locally
    print(f"Starting server on port {port} with auto-reload enabled...")
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=port,
        reload=True,
        reload_dirs=["app"],  # Only watch the app directory
        reload_excludes=["*.log", "*.pyc", "__pycache__"]  # Ignore logs and cache files
    )