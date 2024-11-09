#!/bin/sh

# Avviare il server di autenticazione
python foursquare_auth_server.py &

# Attendere che il token di accesso venga salvato
while [ ! -f "access_token.txt" ] || [ ! -s "access_token.txt" ]; do
  echo "In attesa che il token di accesso venga generato..."
  sleep 5
done

# Avviare il server RSS
python foursquare_checkin_publisher.py
