"""Entry point: `uv run python main.py`. The application itself lives in the app/ package."""
from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
