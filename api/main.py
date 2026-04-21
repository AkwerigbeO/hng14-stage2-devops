from fastapi import FastAPI, HTTPException
import redis
import uuid
import os
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

QUEUE_NAME = os.getenv("QUEUE_NAME", "job")

pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def get_redis():
    return redis.Redis(connection_pool=pool)


r = get_redis()


def check_redis_connection():
    # Only run connection check if not in testing environment
    if os.getenv("TESTING"):
        return
    for i in range(5):
        try:
            r.ping()
            logger.info("Connected to Redis")
            break
        except redis.RedisError:
            logger.warning("Redis not ready, retrying...")
            time.sleep(2)
    else:
        raise Exception("Could not connect to Redis")


check_redis_connection()


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
        r.lpush(QUEUE_NAME, job_id)
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
            raise HTTPException(status_code=404, detail="Job not found")

        logger.info(f"Retrieved job: {job_id} status: {status}")

        return {
            "job_id": job_id,
            "status": status
        }

    except redis.RedisError as e:
        logger.error(f"Failed to get job {job_id}: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable")
