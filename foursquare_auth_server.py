from flask import Flask, request, redirect
import requests
import os

app = Flask(__name__)

FOURSQUARE_CLIENT_ID = os.getenv("FOURSQUARE_CLIENT_ID")
FOURSQUARE_CLIENT_SECRET = os.getenv("FOURSQUARE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")  # URI di reindirizzamento configurato come variabile d'ambiente

@app.route('/')
def home():
    auth_url = f"https://foursquare.com/oauth2/authenticate?client_id={FOURSQUARE_CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
    return f"Please visit the following URL and authorize the application:<br><a href='{auth_url}'>{auth_url}</a>"

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = f"https://foursquare.com/oauth2/access_token?client_id={FOURSQUARE_CLIENT_ID}&client_secret={FOURSQUARE_CLIENT_SECRET}&grant_type=authorization_code&redirect_uri={REDIRECT_URI}&code={code}"
    response = requests.post(token_url)
    token = response.json().get('access_token')
    if token:
        save_token(token)
        return "Access Token saved. You can close this window."
    else:
        return "Failed to obtain access token."

def save_token(token):
    with open("/shared/access_token.txt", "w") as f:  # Salva il token nella cartella condivisa
        f.write(token)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)  # Ascolta su tutte le interfacce
