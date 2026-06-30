FROM node:22-alpine

WORKDIR /app

# Install dependencies first for better caching
COPY package.json .
RUN npm install

# Copy application source code
COPY . .

# Expose port for dev server
EXPOSE 5173

# Launch Vite development server
CMD ["npm", "run", "dev"]
