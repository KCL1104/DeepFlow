import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from deepflow_backend.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
