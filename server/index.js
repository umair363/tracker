# STAGE 1: Build React
FROM node:18-alpine AS build-step
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# STAGE 2: Run Express Server
FROM node:18-alpine
WORKDIR /app
# Copy only what we need from the build stage
COPY --from=build-step /app/dist ./dist
COPY server/ ./server/
COPY package*.json ./
# Install production dependencies for the server
RUN npm install --only=production

EXPOSE 8080
CMD ["node", "server/index.js"]