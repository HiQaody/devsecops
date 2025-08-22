# Use the official Node.js 20 image as the base image
FROM node:20

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install production dependencies only
RUN npm install --production --legacy-peer-deps

# Copy the rest of the application code
COPY . .

# ARG 
ARG NODE_ENV=production
ARG PORT=4002
ARG REACT_APP_API_BASE_URL=http://localhost:4000

# Set environment variables
ENV NODE_ENV=${NODE_ENV}
ENV PORT=${PORT}
ENV REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL}


# Install 'serve' globally to serve the built application
RUN npm install -g serve

# Build the application for production
RUN npm run build

# Expose the port specified in the .env file
EXPOSE ${PORT}

# Start the application using 'serve' to serve the build folder
CMD ["serve", "-s", "build", "-l", "${PORT}"]