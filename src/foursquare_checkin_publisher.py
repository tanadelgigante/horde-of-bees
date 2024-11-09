import os
import requests
from datetime import datetime
from feedgen.feed import FeedGenerator

import json

# Foursquare API credentials from environment variables 
FOURSQUARE_CLIENT_ID = os.getenv("FOURSQUARE_CLIENT_ID") 
FOURSQUARE_CLIENT_SECRET = os.getenv("FOURSQUARE_CLIENT_SECRET")

# Output settings
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT") 
OUTPUT_FILE = os.getenv("OUTPUT_FILE") 

def get_foursquare_checkins(limit=50, offset=0):
    """
    Fetch the latest check-ins from the Foursquare/Swarm API.
    
    Parameters:
    limit (int): Maximum number of check-ins to retrieve
    offset (int): Offset to start retrieving check-ins from
    
    Returns:
    list: List of check-in data
    """
    url = f"https://api.foursquare.com/v2/users/self/checkins"
    params = {
        "client_id": FOURSQUARE_CLIENT_ID,
        "client_secret": FOURSQUARE_CLIENT_SECRET,
        "v": datetime.now().strftime("%Y%m%d"),
        "limit": limit,
        "offset": offset
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    return response.json()["response"]["checkins"]["items"]

def publish_checkins(checkins, output_format):
    """
    Publish the check-in data in the specified output format (RSS or JSON).
    
    Parameters:
    checkins (list): List of check-in data
    output_format (str): Output format ("rss" or "json")
    """
    if output_format == "rss":
        feed = FeedGenerator()
        feed.title("Foursquare Check-ins")
        feed.link({"href": "http://example.com"})
        feed.description("Latest check-ins from Foursquare/Swarm")
        
        for checkin in checkins:
            entry = feed.add_entry()
            entry.title(checkin["venue"]["name"])
            entry.link({"href": f"https://foursquare.com/user/{checkin['user']['id']}/checkin/{checkin['id']}"})
            entry.description(checkin["shout"])
            entry.published(checkin["createdAt"])
            entry.lat(checkin["venue"]["location"]["lat"])
            entry.lon(checkin["venue"]["location"]["lng"])
            if "photos" in checkin and checkin["photos"]["count"] > 0:
                entry.media({"url": checkin["photos"]["items"][0]["prefix"] + "original" + checkin["photos"]["items"][0]["suffix"]})
        
        feed.rss_file(OUTPUT_FILE)
    elif output_format == "json":
        for checkin in checkins:
            checkin["venue"]["location"]["latitude"] = checkin["venue"]["location"]["lat"]
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