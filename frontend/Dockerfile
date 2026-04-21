# Stage 1: Build dependencies
FROM node:20-slim AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci --only=production

# Stage 2: Final production image
FROM node:20-slim

WORKDIR /app

# Create a non-root user
RUN useradd -m appuser

# Install wget for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    rm -rf /var/lib/apt/lists/*

# Copy production dependencies from builder
COPY --from=builder /app/node_modules ./node_modules
COPY package.json ./

# Copy application files and views
COPY app.js .
COPY views/ ./views/

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose frontend port
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --spider -q http://localhost:3000/health || exit 1

CMD ["node", "app.js"]
