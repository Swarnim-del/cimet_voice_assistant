FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

# We will copy the rest of the files via Docker volume in docker-compose for hot-reloading
# but we can copy them here for the initial build context
COPY . .

EXPOSE 5173

# Start Vite dev server on all interfaces so it's accessible outside the container
CMD ["npm", "run", "dev", "--", "--host"]
