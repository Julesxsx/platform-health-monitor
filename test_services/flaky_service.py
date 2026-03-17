import uvicorn
import time
import random
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    if random.random() < 0.3:
        time.sleep(random.uniform(0.4, 0.9))
    else:
        time.sleep(random.uniform(0.05, 0.1))
    return {"status": "ok", "service": "flaky-queue"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)