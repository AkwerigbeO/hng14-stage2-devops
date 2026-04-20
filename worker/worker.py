import redis
import time
import os
import signal
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=False)
r = redis.Redis(connection_pool=pool)

running = True

def sig_handler(signum, frame):
    global running
    logger.info("Graceful shutdown initiated...")
    running = False

signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)

def process_job(job_id):
    logger.info(f"Processing job {job_id}")
    time.sleep(2)  # simulate work
    r.hset(f"job:{job_id}", "status", "completed")
    # Remove from processing queue once done
    r.lrem("job_processing", 0, job_id)
    logger.info(f"Done: {job_id}")

logger.info("Worker started, waiting for jobs...")
while running:
    try:
        # Move job from 'job' queue to 'job_processing' queue reliably
        job_id = r.brpoplpush("job", "job_processing", timeout=5)
        if job_id:
            process_job(job_id.decode())
    except redis.RedisError as e:
        logger.error(f"Redis connection error: {e}")
        time.sleep(2) # Backoff before retrying
    except Exception as e:
        logger.error(f"Unexpected error processing job: {e}")
        time.sleep(1)

logger.info("Worker shutdown complete.")
pool.disconnect()