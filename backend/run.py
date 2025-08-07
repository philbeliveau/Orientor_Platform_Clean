#!/usr/bin/env python
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Force load environment variables BEFORE any other imports
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"✅ Loaded environment from: {env_path}")
else:
    print(f"❌ No .env file found at: {env_path}")
    sys.exit(1)

# Validate critical environment variables
REQUIRED_ENV_VARS = [
    'CLERK_SECRET_KEY',
    'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY',
    'NEXT_PUBLIC_CLERK_DOMAIN'
]

print("\n🔍 Checking required environment variables:")
all_present = True
for var in REQUIRED_ENV_VARS:
    value = os.getenv(var)
    if not value:
        print(f"   ❌ {var}: NOT FOUND")
        all_present = False
    else:
        print(f"   ✅ {var}: {value[:20]}...")

if not all_present:
    print("\n❌ Missing required environment variables!")
    print("   Please check your .env file")
    sys.exit(1)

print("\n✅ All environment variables loaded successfully!\n")

# NOW import the rest
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