import uvicorn
import time
import random
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    time.sleep(random.uniform(0.05, 0.15))
    return {"status": "ok", "service": "api-gateway"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)