# --- STAGE 1: Build the React Application ---
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package management files to leverage layer caching
COPY package*.json ./

# Install frontend dependencies
RUN npm ci

# Copy the rest of the frontend application source files
COPY . .

# Build the production optimized static assets
RUN npm run build

# --- STAGE 2: Serve the Static Assets with Nginx ---
FROM nginx:alpine

# Copy the static production assets from the builder stage over to Nginx's hosting directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 for web traffic
EXPOSE 80

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]