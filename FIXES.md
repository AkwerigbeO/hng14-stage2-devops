# Proposed Fixes

## 1. Group: Frontend

### File: `frontend/app.js`
*   **Line:** 6
*   **Problem:** Hardcoded API URL (`const API_URL = "http://localhost:8000";`) which prevents flexibility when running the API on a different address or port locally.
*   **Fix:** Changed to `const API_URL = process.env.API_URL || "http://localhost:8000";` to allow dynamic overriding via environment variables.

### File: `frontend/app.js`
*   **Line:** 29
*   **Problem:** Hardcoded listening port `3000`.
*   **Fix:** Mapped to use an environment variable with a fallback: `const PORT = process.env.PORT || 3000;`. Replaced `app.listen(3000...)` with `app.listen(PORT...)`.

### File: `frontend/app.js`
*   **Line:** 21, 31
*   **Problem:** Masked root errors within `catch` blocks which return a generic message without printing to stdout, making debugging impossible.
*   **Fix:** Added explicit `console.error` logs before sending the 500 status back to clients.

### File: `frontend/app.js`
*   **Line:** 18, 28
*   **Problem:** Lack of request timeouts in Axios HTTP requests, causing requests to the API to possibly hang indefinitely if the backend is unresponsive.
*   **Fix:** Added a 5000ms timeout parameter to both calls: `{ timeout: 5000 }`.

### File: `frontend/app.js`
*   **Line:** 12
*   **Problem:** Missing endpoint to verify the health and connectivity of the frontend service.
*   **Fix:** Implemented a new root endpoint: `app.get('/health', (req, res) => res.status(200).send('OK'));`.

---

## 2. Group: Backend API

### File: `api/main.py`
*   **Line:** 15
*   **Problem:** Hardcoded Redis connection parameters limit the ability to connect to external Redis instances.
*   **Fix:** Used `os.getenv` allowing `REDIS_HOST`, `REDIS_PORT`, and `REDIS_PASSWORD` to be configured via environment variables. Added `python-dotenv` to load local `.env` files.

### File: `api/main.py`
*   **Line:** 20
*   **Problem:** Missing connection pool initialization, leading to inefficient connection handling.
*   **Fix:** Initialized a Redis `ConnectionPool` to manage connections efficiently and prevent resource leaks.

### File: `api/main.py`
*   **Line:** 28, 40, 52
*   **Problem:** Missing error handling on Redis operations. Network interruptions or Redis downtime crash the API.
*   **Fix:** Embedded `try/except redis.RedisError` blocks around operations to return `503 Service Unavailable` instead of crashing.

### File: `api/main.py`
*   **Line:** 10
*   **Problem:** Lack of application-level logging.
*   **Fix:** Configured the `logging` package to track success and errors, routing output to `stdout`.

### File: `api/main.py`
*   **Line:** 23
*   **Problem:** No endpoint to verify API and Redis connectivity.
*   **Fix:** Integrated a `/health` endpoint that performs an `r.ping()` to verify the database connection.

---

## 3. Group: Worker Service

### File: `worker/worker.py`
*   **Line:** 14
*   **Problem:** Hardcoded Redis configuration prevents connecting to any instance other than localhost.
*   **Fix:** Implemented dynamic environment variable loading (`REDIS_HOST`, `REDIS_PORT`, etc.) via `python-dotenv`.

### File: `worker/worker.py`
*   **Line:** 41
*   **Problem:** Unsafe execution loop; unhandled exceptions cause the worker to crash and stop processing.
*   **Fix:** Wrapped the main loop in a `try/except` block to log errors and continue running.

### File: `worker/worker.py`
*   **Line:** 43
*   **Problem:** Destructive job retrieval logic via `brpop`. If the worker crashes during processing, the job is lost forever.
*   **Fix:** Transitioned to `brpoplpush` to move jobs to a `job_processing` list, ensuring they can be recovered if the worker fails.

### File: `worker/worker.py`
*   **Line:** 23-29
*   **Problem:** Lack of graceful shutdown handling.
*   **Fix:** Added signal handlers for `SIGINT` and `SIGTERM` to allow the worker to finish the current job and close connections before exiting.
