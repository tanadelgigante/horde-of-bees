from flask import Flask, request, Response
import requests
import os
import time
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import threading
import re

app = Flask(__name__)

# Output settings
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT")
OUTPUT_FILE = "/shared/check_ins.xml"  # Salva il file nella cartella condivisa
SERVER_URL = os.getenv("SERVER_URL")
TOKEN_FILE_PATH = "/shared/access_token.txt"

def read_token():
    while not os.path.exists(TOKEN_FILE_PATH) or os.stat(TOKEN_FILE_PATH).st_size == 0:
        print("In attesa che il token di accesso venga generato...")
        time.sleep(5)
    with open(TOKEN_FILE_PATH, "r") as f:
        return f.read().strip()

API_TOKEN = read_token()

def get_foursquare_checkins(limit=50, offset=0):
    url = f"https://api.foursquare.com/v2/users/self/checkins"
    params = {
        "oauth_token": API_TOKEN,
        "v": datetime.now().strftime("%Y%m%d"),
        "limit": limit,
        "offset": offset
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    return response.json()["response"]["checkins"]["items"]

def generate_rss_feed():
    checkins = get_foursquare_checkins()
    feed = FeedGenerator()
    feed.title("Foursquare Check-ins")
    feed.link(href=SERVER_URL, rel='alternate')  # Usa SERVER_URL dalla variabile d'ambiente
    feed.description("Latest check-ins from Foursquare/Swarm")
    
    for checkin in checkins:
        entry = feed.add_entry()
        if 'venue' in checkin and 'name' in checkin['venue']:
            entry.title(checkin['venue']['name'])
        if 'venue' in checkin and 'id' in checkin['venue']:
            entry.link({"href": f"https://foursquare.com/v/{checkin['venue']['id']}"})
        if 'shout' in checkin:
            entry.description(checkin['shout'])
        description = ""
        if 'createdAt' in checkin:
            entry.published(datetime.fromtimestamp(checkin['createdAt'], timezone.utc))  # Aggiungi informazioni sul fuso orario
        if 'venue' in checkin and 'location' in checkin['venue']:
            if 'lat' in checkin['venue']['location'] and 'lng' in checkin['venue']['location']:
                description += f"Lat: {checkin['venue']['location']['lat']}, Lon: {checkin['venue']['location']['lng']}"
        if "photos" in checkin and checkin["photos"]["count"] > 0:
            entry.media({"url": checkin["photos"]["items"][0]["prefix"] + "original" + checkin["photos"]["items"][0]["suffix"]})
        if description:
            entry.description(description)

    # Genera il feed RSS e sostituisci l'intera riga con l'intestazione richiesta
    rss_feed = feed.rss_str(pretty=True)
    rss_feed = rss_feed.decode('utf-8')
    rss_feed = re.sub(r'<rss[^>]+>', '<rss xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">', rss_feed, 1)

    with open(OUTPUT_FILE, 'w') as f:
        f.write(rss_feed)
    
    print(f"RSS feed updated at {datetime.now()}")

@app.route('/rss')
@app.route('/rss/')
def serve_rss_feed():
    with open(OUTPUT_FILE, 'r') as f:
        rss_feed = f.read()
    return Response(rss_feed, mimetype='application/rss+xml')

def update_feed_regularly():
    while True:
        generate_rss_feed()
        time.sleep(1800)  # Attendere 30 minuti (1800 secondi) prima del prossimo aggiornamento

if __name__ == '__main__':
    if os.path.exists(TOKEN_FILE_PATH) and os.stat(TOKEN_FILE_PATH).st_size > 0:
        API_TOKEN = read_token()
    else:
        print("Token non trovato, arresto del server.")
        sys.exit()
    
    threading.Thread(target=update_feed_regularly).start()
    app.run(host='0.0.0.0', port=8000)
