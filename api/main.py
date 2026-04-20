from fastapi import FastAPI, HTTPException
import redis
import uuid
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Use connection pool for better resource management
pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=False)
r = redis.Redis(connection_pool=pool)

@app.get("/health")
def health_check():
    try:
        r.ping()
        return {"status": "healthy", "redis": "connected"}
    except redis.RedisError as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable")

@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    try:
        r.lpush("job", job_id)
        r.hset(f"job:{job_id}", "status", "queued")
        logger.info(f"Created job: {job_id}")
        return {"job_id": job_id}
    except redis.RedisError as e:
        logger.error(f"Failed to create job {job_id}: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable")

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    try:
        status = r.hget(f"job:{job_id}", "status")
        if not status:
            return {"error": "not found"}
        logger.info(f"Retrieved job: {job_id} status: {status.decode()}")
        return {"job_id": job_id, "status": status.decode()}
    except redis.RedisError as e:
        logger.error(f"Failed to get job {job_id}: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable")
