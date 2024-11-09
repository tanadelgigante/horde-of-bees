from flask import Flask, request, redirect
import requests  
import os

app = Flask(__name__)

FOURSQUARE_CLIENT_ID = os.getenv("FOURSQUARE_CLIENT_ID")
FOURSQUARE_CLIENT_SECRET = os.getenv("FOURSQUARE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"

@app.route('/')
def home():
    return 'Foursquare OAuth 2.0'

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = f"https://foursquare.com/oauth2/access_token?client_id={FOURSQUARE_CLIENT_ID}&client_secret={FOURSQUARE_CLIENT_SECRET}&grant_type=authorization_code&redirect_uri={REDIRECT_URI}&code={code}"
    response = requests.post(token_url)
    token = response.json().get('access_token')
    if token:
        save_token(token)
        return f"Access Token: {token}"
    else:
        return "Failed to obtain access token."

def save_token(token):
    with open("access_token.txt", "w") as f:
        f.write(token)

if __name__ == '__main__':
    app.run(port=8000)
