# Base image for Node.js
FROM node:16

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the React app for production
RUN npm run build

# Install a simple HTTP server to serve static files
RUN npm install -g serve

# Expose the port the application runs on
EXPOSE 3030

# Start the server
CMD ["serve", "-s", "build" "-l", "3030"]
