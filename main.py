from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import time
import uvicorn

from agent import run_agent
from shared_store import url_time, BASE64_STORE

load_dotenv()

EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()

@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "uptime_seconds": int(time.time() - START_TIME)
    }

# Evaluator may call "/" or "/solve"
@app.post("/")
@app.post("/solve")
async def solve(request: Request, background_tasks: BackgroundTasks):
    # ---- Parse JSON ----
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Invalid JSON")

    url = data.get("url")
    secret = data.get("secret")

    if not url or not secret:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # ---- Secret validation ----
    if secret != SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    # ---- Reset shared state ----
    url_time.clear()
    BASE64_STORE.clear()

    # ---- Seed environment for agent ----
    os.environ["url"] = url
    os.environ["offset"] = "0"
    url_time[url] = time.time()

    # ---- Run agent asynchronously ----
    background_tasks.add_task(run_agent, url)

    return JSONResponse(status_code=200, content={"status": "ok"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
