# Dockerfile for Node.js server on Hugging Face Spaces
FROM node:18

# Create a user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy package files
COPY --chown=user package*.json ./
RUN npm install

# Copy the rest
COPY --chown=user . /app

# Expose port 7860
EXPOSE 7860

# Start the server
CMD ["node", "server.js"]