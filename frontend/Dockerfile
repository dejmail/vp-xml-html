# Base image for Node.js
FROM node:18

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the React app for production (optional if using production build)
RUN npm run build

RUN chown -R node:node /app

USER node

# Expose the port the application runs on
EXPOSE 3030

# Set environment variables
ENV PORT 3030

# Start the server and bind to 0.0.0.0
CMD ["npm", "start", "--", "--host", "0.0.0.0"]

