# Horde of Bees - RSS & Auth Servers

## Descrizione

Horde of Bees è un'applicazione composta da due server: un server di autenticazione e un server RSS. Il server di autenticazione gestisce l'autenticazione tramite Foursquare e il server RSS genera e serve un feed RSS basato sui check-in di Foursquare.

## Uso

Occorre innanzitutto registrare una nuova App sul sito per sviluppatori di Foursquare (https://it.foursquare.com/developers/home), avrete 200'000 crediti gratis. Qui registrerete la vostra installazione di Horde of Bees e configurerete la parte di autenticazione "OAuth Authentication". Da qui preleverete il FOURSQUARE_CLIENT_ID, il FOURSQUARE_CLIENT_SECRET e imposterete la REDIRECT_URI (le stesse della configurazione qui di seguito).
Inoltre il vostro server di autenticazione dovrà essere esposto su Internet (perché Fourquare vi dovrà chiamare all'indirizzo di callback) e sarà attivo fintantoché la procedura di autenticazione non sarà conclusa. Successivamente si disattiverà da solo.
Invece il vostro server RSS potrà anche restare privato e non esposto sulla rete pubblica. 

## Requisiti

- Docker
- Docker Compose

## Installazione

1. Clona il repository:

    ```sh
    git clone https://github.com/username/HordeOfBees.git
    cd HordeOfBees
    ```

2. Crea un file `.env` nella directory principale del progetto e aggiungi le seguenti variabili d'ambiente:

    ```env
    FOURSQUARE_CLIENT_ID=your_client_id
    FOURSQUARE_CLIENT_SECRET=your_client_secret
    REDIRECT_URI=https://your_redirect_uri/callback/
    ```

3. Costruisci e avvia i container Docker:

    ```sh
    docker-compose up --build
    ```

4. Visita `http://localhost:7777` per avviare il processo di autenticazione. Dopo aver autenticato l'applicazione, il server di autenticazione si arresterà automaticamente.

5. Visita `http://localhost:7778` per accedere al feed RSS.

## Docker Compose

Il file `docker-compose.yml` avvia due servizi Docker:

- `horde-auth`: gestisce l'autenticazione tramite Foursquare.
- `horde-rss`: genera e serve il feed RSS.

## Licenza

Questo progetto è concesso in licenza sotto i termini della [GNU General Public License v3.0 o successiva](LICENSE).

## Disclaimer

Questo componente non è affiliato né correlato agli sviluppatori di Foursquare o Swarm ed è utilizzato per lo studio delle capacità delle API della piattaforma. Questo componente è fornito "così com'è" e l'autore non è responsabile per eventuali malfunzionamenti o danni ai tuoi sistemi. Ogni collaborazione è benvenuta.

---

# Horde of Bees - RSS & Auth Servers

## Description

Horde of Bees is an application composed of two servers: an authentication server and an RSS server. The authentication server handles authentication via Foursquare, and the RSS server generates and serves an RSS feed based on Foursquare check-ins.

## Usage

First, you need to register a new App on the Foursquare developers site (https://foursquare.com/developers/home), where you will get 200,000 free credits. Here you will register your installation of Horde of Bees and configure the "OAuth Authentication" part. From here, you will retrieve the FOURSQUARE_CLIENT_ID, the FOURSQUARE_CLIENT_SECRET, and set the REDIRECT_URI (the same as the configuration below). Additionally, your authentication server will need to be exposed on the Internet (because Foursquare will need to call you at the callback address), and it will be active until the authentication process is complete. Afterwards, it will deactivate itself. However, your RSS server can remain private and does not need to be exposed to the public network.

## Requirements

- Docker
- Docker Compose

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/username/HordeOfBees.git
    cd HordeOfBees
    ```

2. Create a `.env` file in the project's root directory and add the following environment variables:

    ```env
    FOURSQUARE_CLIENT_ID=your_client_id
    FOURSQUARE_CLIENT_SECRET=your_client_secret
    REDIRECT_URI=https://your_redirect_uri/callback/
    ```

3. Build and start the Docker containers:

    ```sh
    docker-compose up --build
    ```

4. Visit `http://localhost:7777` to start the authentication process. After authenticating the application, the authentication server will automatically shut down.

5. Visit `http://localhost:7778` to access the RSS feed.

## Docker Compose

The `docker-compose.yml` file starts two Docker services:

- `horde-auth`: handles authentication via Foursquare.
- `horde-rss`: generates and serves the RSS feed.

## License

This project is licensed under the terms of the [GNU General Public License v3.0 or later](LICENSE).

## Disclaimer

This component is not affiliated or related to Foursquare or Swarm developers and is used for study of the platform API capabilities. This component is intended "as-is" and the author is not responsible for malfunctioning or damaging of your systems. Any collaboration is welcome.
