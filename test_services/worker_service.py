import uvicorn
import time
import random
from fastapi import FastAPI, Response

app = FastAPI()
request_count = 0

@app.get("/health")
def health(response: Response):
    global request_count
    request_count += 1
    if request_count % 5 == 0:
        response.status_code = 503
        return {"status": "down", "service": "worker"}
    time.sleep(random.uniform(0.1, 0.3))
    return {"status": "ok", "service": "worker"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)