import os
import time
import requests
from datetime import datetime
from feedgen.feed import FeedGenerator
import json

# Attendere fino a quando il token di accesso non è disponibile
while not os.path.exists("/shared/access_token.txt") or os.stat("/shared/access_token.txt").st_size == 0:
    print("In attesa che il token di accesso venga generato...")
    time.sleep(5)

# Leggere il token di accesso
with open("/shared/access_token.txt", "r") as f:
    API_TOKEN = f.read().strip()

# Output settings
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT")
OUTPUT_FILE = os.getenv("OUTPUT_FILE")
SERVER_URL = os.getenv("SERVER_URL")  # Aggiungi l'indirizzo del server come variabile d'ambiente

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

def publish_checkins(checkins, output_format):
    if output_format == "rss":
        feed = FeedGenerator()
        feed.title("Foursquare Check-ins")
        feed.link({"href": SERVER_URL})  # Usa l'indirizzo del server
        feed.description("Latest check-ins from Foursquare/Swarm")
        
        for checkin in checkins:
            entry = feed.add_entry()
            if 'venue' in checkin and 'name' in checkin['venue']:
                entry.title(checkin['venue']['name'])
            if 'venue' in checkin and 'id' in checkin['venue']:
                entry.link({"href": f"https://foursquare.com/v/{checkin['venue']['id']}"})
            if 'shout' in checkin:
                entry.description(checkin['shout'])
            if 'createdAt' in checkin:
                entry.published(datetime.utcfromtimestamp(checkin['createdAt']))
            if 'venue' in checkin and 'location' in checkin['venue']:
                if 'lat' in checkin['venue']['location']:
                    entry.lat(checkin['venue']['location']['lat'])
                if 'lng' in checkin['venue']['location']:
                    entry.lon(checkin['venue']['location']['lng'])
            if "photos" in checkin and checkin["photos"]["count"] > 0:
                entry.media({"url": checkin["photos"]["items"][0]["prefix"] + "original" + checkin["photos"]["items"][0]["suffix"]})
        
        feed.rss_file(OUTPUT_FILE)
    elif output_format == "json":
        for checkin in checkins:
            if 'venue' in checkin and 'location' in checkin['venue']:
                if 'lat' in checkin['venue']['location']:
                    checkin["venue"]["location"]["latitude"] = checkin["venue"]["location"]["lat"]
                if 'lng' in checkin['venue']['location']:
                    checkin["venue"]["location"]["longitude"] = checkin["venue"]["location"]["lng"]
            if "photos" in checkin and checkin["photos"]["count"] > 0:
                checkin["photo_url"] = checkin["photos"]["items"][0]["prefix"] + "original" + checkin["photos"]["items"][0]["suffix"]
        
        with open(OUTPUT_FILE, "w") as f:
            json.dump(checkins, f, indent=2)
    else:
        raise ValueError("Invalid output format. Use 'rss' or 'json'.")

def main():
    checkins = get_foursquare_checkins()
    publish_checkins(checkins, OUTPUT_FORMAT)
    print(f"Check-ins published to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
