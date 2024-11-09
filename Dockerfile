FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the scripts
COPY src/foursquare_auth_server.py .
COPY src/foursquare_checkin_publisher.py .
COPY src/start_servers.sh .

# Install dependencies
RUN pip install --no-cache-dir requests feedgen flask

# Expose the ports
EXPOSE 8000 8080

# Run the startup script
CMD ["sh", "start_servers.sh"]
