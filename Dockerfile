### Multi-stage Dockerfile
### Builds frontend (Vite) and backend (TypeScript) and runs the compiled backend

FROM node:20-alpine AS builder
WORKDIR /workspace

# Install frontend deps and build
COPY web/frontend/package*.json web/frontend/
RUN cd web/frontend && npm ci
COPY web/frontend web/frontend
RUN cd web/frontend && npm run build

# Install backend deps and build
COPY web/backend/package*.json web/backend/
RUN cd web/backend && npm ci
COPY web/backend web/backend

# Copy data needed by backend (resume.yaml)
COPY data data

# Copy the built frontend into the workspace (so backend can reference its path)
# (Vite output is at web/frontend/dist)
RUN cp -r web/frontend/dist web/frontend/dist || true

# Build backend (compiles TypeScript -> dist)
RUN cd web/backend && npm run build

FROM node:20-alpine AS runtime
WORKDIR /app

# Keep the same web/ layout expected by the server code
COPY --from=builder /workspace/web ./web
COPY --from=builder /workspace/data ./data

# Install only production deps for backend
COPY web/backend/package*.json ./web/backend/
WORKDIR /app/web/backend
RUN npm ci --production

ENV NODE_ENV=production
ENV PORT_BACKEND=8080
EXPOSE 8080

# Start the compiled backend server. It expects compiled JS at web/backend/dist
CMD ["node", "dist/server.js"]
