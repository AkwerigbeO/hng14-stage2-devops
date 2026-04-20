# Stage 1: Build dependencies
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production

# Stage 2: Final production image
FROM node:20-alpine

WORKDIR /app

# Use the pre-existing 'node' user provided by the alpine image
# Ensure the app directory is owned by the node user
RUN chown -R node:node /app

# Copy production dependencies from builder
COPY --from=builder /app/node_modules ./node_modules
COPY package.json ./

# Copy application files and views
COPY app.js .
COPY views/ ./views/

# Switch to non-root user
USER node

# Expose frontend port
EXPOSE 3000

# Environment variables
ENV PORT=3000
ENV API_URL=http://api:8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:' + (process.env.PORT || 3000) + '/health', (res) => { if (res.statusCode !== 200) process.exit(1); })" || exit 1

CMD ["node", "app.js"]
