from flask import Flask, request, redirect, send_file, url_for
import requests
import os
from io import BytesIO
import sys
import json

app = Flask(__name__)

# Carica nome e versione dal file manifest.json
with open('manifest.json') as f:
    manifest = json.load(f)
    app_name = manifest['name'] + " - Auth Helper Server"
    app_version = manifest['version']

print(f"Starting {app_name} version {app_version}")

# Ottieni le variabili d'ambiente
FOURSQUARE_CLIENT_ID = os.getenv("FOURSQUARE_CLIENT_ID")
FOURSQUARE_CLIENT_SECRET = os.getenv("FOURSQUARE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")  # URI di reindirizzamento configurato come variabile d'ambiente
TOKEN_FILE_PATH = "/shared/access_token.txt"

# Funzione per assicurarsi che la REDIRECT_URI abbia la barra finale
def ensure_trailing_slash(uri):
    if not uri.endswith('/'):
        return uri + '/'
    return uri

# Applicare la funzione alla REDIRECT_URI
REDIRECT_URI = ensure_trailing_slash(REDIRECT_URI)

@app.route('/')
def home():
    # Controlla se il file del token esiste e ha contenuto
    if os.path.exists(TOKEN_FILE_PATH) and os.stat(TOKEN_FILE_PATH).st_size > 0:
        print("Token già presente. Arresto del server.")
        shutdown_server()
    # Genera l'URL di autenticazione
    auth_url = f"https://foursquare.com/oauth2/authenticate?client_id={FOURSQUARE_CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
    print(f"Auth URL: {auth_url}")
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{app_name}</title>
        <link rel="stylesheet" href="{url_for('static', filename='horde.css')}">
    </head>
    <body>
        <header>
            <h1>{app_name}</h1>
        </header>
        <div class="container">
            <p>Please visit the following URL and authorize the application:</p>
            <a href='{auth_url}'>{auth_url}</a>
        </div>
        <footer>
            <p>&copy; {datetime.now().year} {app_name}</p>
        </footer>
    </body>
    </html>
    """

@app.route('/callback')
@app.route('/callback/')
def callback():
    # Ottieni il codice di autorizzazione dalla richiesta
    code = request.args.get('code')
    print(f"Received auth code: {code}")
    # Genera l'URL per ottenere l'access token
    token_url = f"https://foursquare.com/oauth2/access_token?client_id={FOURSQUARE_CLIENT_ID}&client_secret={FOURSQUARE_CLIENT_SECRET}&grant_type=authorization_code&redirect_uri={REDIRECT_URI}&code={code}"
    # Richiedi l'access token
    response = requests.post(token_url)
    token = response.json().get('access_token')
    if token:
        save_token(token)
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Access Token Saved</title>
            <link rel="stylesheet" href="{url_for('static', filename='horde.css')}">
        </head>
        <body>
            <header>
                <h1>Access Token Saved</h1>
            </header>
            <div class="container">
                <p>You can close this window.</p>
            </div>
            <footer>
                <p>&copy; {datetime.now().year} {app_name}</p>
            </footer>
        </body>
        </html>
        """
    else:
        print("Failed to obtain access token.")
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Access Token Failed</title>
            <link rel="stylesheet" href="{url_for('static', filename='horde.css')}">
        </head>
        <body>
            <header>
                <h1>Failed to Obtain Access Token</h1>
            </header>
            <div class="container">
                <p>There was an error obtaining the access token. Please try again.</p>
            </div>
            <footer>
                <p>&copy; {datetime.now().year} {app_name}</p>
            </footer>
        </body>
        </html>
        """

@app.route('/favicon.ico')
def favicon():
    # Restituisci una favicon di default
    img = BytesIO()
    img.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x10\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00')
    img.seek(0)
    return send_file(img, mimetype='image/vnd.microsoft.icon')

def save_token(token):
    # Salva l'access token nel file
    with open(TOKEN_FILE_PATH, "w") as f:
        f.write(token)
    print("Token salvato. Arresto del server.")
    shutdown_server()

def shutdown_server():
    # Arresta il server Flask
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Non è possibile arrestare il server.')
    func()

if __name__ == '__main__':
    # Controlla se il file del token esiste e ha contenuto, altrimenti avvia il server
    if os.path.exists(TOKEN_FILE_PATH) and os.stat(TOKEN_FILE_PATH).st_size > 0:
        print("Token già presente. Arresto del server.")
        sys.exit()
    print(f"{app_name} server in esecuzione su http://0.0.0.0:8000")
    app.run(host='0.0.0.0', port=8000)
