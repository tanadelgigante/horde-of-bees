FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the script
COPY src/foursquare_checkin_publisher.py .

# Install dependencies
RUN pip install --no-cache-dir requests feedgen 

# Expose the port
EXPOSE 8080

# Run the script
CMD ["python", "foursquare_checkin_publisher.py"]
