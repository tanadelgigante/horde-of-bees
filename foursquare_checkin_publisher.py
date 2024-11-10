from flask import Flask, request, Response, send_file, url_for
import requests
import os
import time
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import threading
import re
import json
from io import BytesIO

app = Flask(__name__)

# Carica nome e versione dal file manifest.json
with open('manifest.json') as f:
    manifest = json.load(f)
    APP_NAME = manifest.get("name")
    APP_VERSION = manifest.get("version")

print(f"Starting {APP_NAME} - RSS Server version {APP_VERSION}")

# Impostazioni di output
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT")
OUTPUT_FILE = "/shared/check_ins.xml"  # Salva il file nella cartella condivisa
SERVER_URL = os.getenv("SERVER_URL")
TOKEN_FILE_PATH = "/shared/access_token.txt"

# Funzione per leggere il token di accesso
def read_token():
    while not os.path.exists(TOKEN_FILE_PATH) or os.stat(TOKEN_FILE_PATH).st_size == 0:
        print("In attesa che il token di accesso venga generato...")
        time.sleep(5)
    with open(TOKEN_FILE_PATH, "r") as f:
        return f.read().strip()

# Leggi il token di accesso
API_TOKEN = read_token()

# Funzione per recuperare i check-in da Foursquare
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

# Funzione per generare il feed RSS
def generate_rss_feed():
    print("Generating RSS feed...")
    checkins = get_foursquare_checkins()
    feed = FeedGenerator()
    feed.title("Latest check-ins from Foursquare/Swarm")
    feed.link(href=SERVER_URL, rel='self')
    feed.description("This is the RSS feed of latest check-ins from Foursquare/Swarm.")
    feed.generator("python-feedgen")
    feed.pubDate(datetime.now(timezone.utc))

    for checkin in checkins:
        entry = feed.add_entry()
        if 'venue' in checkin and 'name' in checkin['venue']:
            entry.title("Check-in: " + checkin['venue']['name'])
        if 'venue' in checkin and 'id' in checkin['venue']:
            entry.link(href=f"https://foursquare.com/v/{checkin['venue']['id']}")
        if 'shout' in checkin:
            entry.description(checkin['shout'])
        description = ""
        if 'createdAt' in checkin:
            entry.pubDate(datetime.fromtimestamp(checkin['createdAt'], timezone.utc))
        if 'venue' in checkin and 'location' in checkin['venue']:
            if 'lat' in checkin['venue']['location'] and 'lng' in checkin['venue']['location']:
                description += f"Coordinates: ({checkin['venue']['location']['lat']}, {checkin['venue']['location']['lng']})"
        if description:
            entry.description(description)
    
    # Genera il feed RSS e sostituisci l'intera riga con l'intestazione richiesta
    rss_feed = feed.rss_str(pretty=True)
    rss_feed = rss_feed.decode('utf-8')
    rss_feed = re.sub(r'<rss[^>]+>', '<rss xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">', rss_feed, 1)

    with open(OUTPUT_FILE, 'w') as f:
        f.write(rss_feed)
    
    print(f"RSS feed updated at {datetime.now()}")
    return rss_feed

@app.route('/')
def home():
    # Genera il feed RSS e restituiscilo
    rss_feed = generate_rss_feed()
    rss_display = ""
    for entry in re.findall(r'<item>(.*?)</item>', rss_feed, re.DOTALL):
        title = re.search(r'<title>(.*?)</title>', entry).group(1)
        link = re.search(r'<link>(.*?)</link>', entry).group(1)
        description = re.search(r'<description>(.*?)</description>', entry).group(1)
        pubDate = re.search(r'<pubDate>(.*?)</pubDate>', entry).group(1)
        rss_display += f"""
        <div class="rss-entry">
            <h3>{title}</h3>
            <p><a href="{link}">{link}</a></p>
            <p>{description}</p>
            <p>When: {pubDate}</p>
        </div>
        <hr>
        """
    server_info = f"Server: {SERVER_URL}<br>Created by: python-feedgen<br>Update: {datetime.now().strftime('%a, %d %b %Y %H:%M')}"

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{APP_NAME}</title>
        <link rel="stylesheet" href="{url_for('static', filename='horde.css')}">
        <style>
            pre {{
                background-color: #f8f8f8;
                padding: 10px;
                border: 1px solid #ddd;
                overflow-x: auto;
            }}
            .icon {{
                margin-right: 5px;
            }}
            .rss-entry {{
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>{APP_NAME}</h1>
        </header>
        <div class="container">
            <h2>Latest check-ins from Foursquare/Swarm</h2>
            <p>{server_info}</p>
            {rss_display}
            <a href="{url_for('download_rss')}" class="button">
                <span class="icon">&#128229;</span> Download RSS
            </a>
            <a href="{SERVER_URL}" class="button">
                <span class="icon">&#128240;</span> Subscribe to RSS
            </a>
        </div>
        <footer>
            <p>&copy; {datetime.now().year} {APP_NAME}</p>
        </footer>
    </body>
    </html>
    """

@app.route('/rss')
@app.route('/rss/')
def serve_rss_feed():
    with open(OUTPUT_FILE, 'r') as f:
        rss_feed = f.read()
    return Response(rss_feed, mimetype='application/rss+xml')

@app.route('/download')
def download_rss():
    return send_file(OUTPUT_FILE, as_attachment=True, attachment_filename='check_ins.xml')

def update_feed_regularly():
    while True:
        generate_rss_feed()
        time.sleep(1800)  # Attendere 30 minuti (1800 secondi) prima del prossimo aggiornamento

if __name__ == '__main__':
    print(f"Starting {APP_NAME} v{APP_VERSION}")
    if os.path.exists(TOKEN_FILE_PATH) and os.stat(TOKEN_FILE_PATH).st_size > 0:
        API_TOKEN = read_token()
    else:
        print("Token non trovato, arresto del server.")
        sys.exit()
    
    threading.Thread(target=update_feed_regularly).start()
    app.run(host='0.0.0.0', port=8000)
