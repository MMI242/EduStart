# Use Node.js as the base image
FROM node:20-slim

# Set the working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5173

# Start the application in development mode
# Use --host to ensure it's accessible outside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
