FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the script
COPY src/foursquare_checkin_publisher.py .

# Install dependencies
RUN pip install --no-cache-dir os requests datetime feedgen json 

# Set environment variables
ENV FOURSQUARE_CLIENT_ID=your_client_id
ENV FOURSQUARE_CLIENT_SECRET=your_client_secret 
ENV OUTPUT_FORMAT=rss
ENV OUTPUT_FILE=/app/check_ins.xml
ENV PORT=8080

# Expose the port
EXPOSE $PORT

# Run the script
CMD ["python", "foursquare_checkin_publisher.py"]