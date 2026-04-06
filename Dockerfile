# ─── Stage 1: Build the React app ────────────────────────────────────────────
FROM node:18-alpine AS builder
WORKDIR /app

# Pass Supabase credentials as build-time args so Vite can bake them in
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY

# Install ALL dependencies (including devDependencies like vite)
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build

# ─── Stage 2: Serve with Express ─────────────────────────────────────────────
FROM node:18-alpine
WORKDIR /app

COPY package*.json ./
RUN npm install --only=production

# Copy built app and server from previous stage
COPY --from=builder /app/dist ./dist
COPY server/ ./server/

EXPOSE 8080
CMD ["node", "server/index.js"]