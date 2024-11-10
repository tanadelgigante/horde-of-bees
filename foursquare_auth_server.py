from flask import Flask, request, redirect
import requests
import os

app = Flask(__name__)

FOURSQUARE_CLIENT_ID = os.getenv("FOURSQUARE_CLIENT_ID")
FOURSQUARE_CLIENT_SECRET = os.getenv("FOURSQUARE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")  # URI di reindirizzamento configurato come variabile d'ambiente


# Funzione per assicurarsi che la REDIRECT_URI abbia la barra finale 
def ensure_trailing_slash(uri): 
    if not uri.endswith('/'): 
        return uri + '/' 
    return uri 


# Applicare la funzione alla REDIRECT_URI 
REDIRECT_URI = ensure_trailing_slash(REDIRECT_URI)


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

    
@app.route('/favicon.ico') 
def favicon(): 
    img = BytesIO() 
    img.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x10\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00') 
    img.seek(0) 
    return send_file(img, mimetype='image/vnd.microsoft.icon')


def save_token(token):
    with open("/shared/access_token.txt", "w") as f:  # Salva il token nella cartella condivisa
        f.write(token)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)  # Ascolta su tutte le interfacce
