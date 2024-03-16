import uvicorn
from fastapi import FastAPI

app = FastAPI()

if __name__ == "__main__":
    # Run the app
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
