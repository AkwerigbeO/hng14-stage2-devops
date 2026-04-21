# HNG14 Stage 2 DevOps Architecture

This repository holds a simulated microservice architecture consisting of a Python FastAPI backend, a Python background worker, a Node.js Express frontend, and a Redis message queue. 

It is fully containerized with Docker, thoroughly linted, and governed by a strict 6-stage GitHub Actions CI/CD pipeline covering dynamic artifact-passing and automated Trivy Security scans.

## Startup Instructions (Clean Machine)

If you are pulling this codebase down to a completely fresh machine, follow these directions to quickly orchestrate the complete stack using our unified Docker Compose configuration.

### 1. Prerequisites
Ensure you have the following installed on your host system:
1. **Docker Desktop** or **Docker Engine** (v24.0.0 or higher)
2. **Docker Compose plugin** (v2.20.0 or higher)
3. **Git** (to clone the repository)

*Note: You do not need Python or Node.js installed natively to run this stack, as everything executes within completely isolated Linux containers.*

### 2. Startup Commands
Open your terminal and run the following commands sequentially:

```bash
# Clone the repository
git clone https://github.com/AkwerigbeO/hng14-stage2-devops.git
cd hng14-stage2-devops

# Generate the local environment variables from the template
cp .env.example .env

# Build and launch the stack in detached mode
docker compose up -d --build
```

### 3. What a Successful Startup Looks Like
Docker Compose will download the base images (Python, Node, Redis) and build `frontend`, `api`, and `worker`. 

Because we have strictly coupled the initialization using `depends_on: condition: service_healthy`, you will observe the startup in exactly this order:
1. `redis` spins up.
2. The `api` and `worker` containers hold until `redis` registers internally as `Healthy` (can be pinged).
3. The `frontend` container holds until `api` registers as `Healthy` (HTTP `/health` check passes).

**To verify it worked:**
```bash
docker compose ps
```
All four containers (`redis`, `api`, `worker`, `frontend`) should display an **`Up (healthy)`** or **`Up`** status.

You can now interact with the frontend at: `http://localhost:3000`
You can ping the backend healthcheck directly at: `http://localhost:8000/health`

### Shutting Down
To gracefully stop and destroy the containers and network interfaces without deleting the underlying persistent volumes:
```bash
docker compose down
```

## Bug Fixes & Architecture Details
During the initial debugging phase of this project, several architectural, network, and application-level bugs were identified and resolved across the Node.js frontend, Python FastAPI backend, and Redis worker. 

For a complete, line-by-line breakdown of every bug discovered and the methodology used to fix it, please refer to the [FIXES.md](./FIXES.md) document in this repository.
