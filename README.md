# CCNY_Database_Project_Variation

This is a modified repo of the CCNY_Database_Project modified to used SQLAlchemy with sqlite. This project can be used to track your albums that you have collected in the form of physical media. It uses Spotify data via the Spotipy library to search albums. SQLite and Flask are used for the backend.

## Requirements 

- [Python](https://www.python.org/downloads/)
- Free Spotify account to access [developer tools](https://developer.spotify.com/dashboard/)

## Instructions to run on your computer

1. Set up python virtual environment: 
    
    Create environment: 
    ```bash
    python3 -m venv env
    ```

    Activate environment:

    - on Windows: 
        ```bash
        env\scripts\activate
        ```

    - on Mac: 
        ```bash
        env/bin/activate
        ```

2. Install required packages: 
    ```bash
    pip install -r requirements.txt
    ```

3. In `flask_app` folder, create a `.env` file with the following variables:
    
    Key of your choice 
    ```sh
    SECRET_KEY =
    ``` 
    
    Create an app in your Spotify developer dashboard and use the client id and client secret from that app.
    ```sh
    SPOTIFY_CLIENT_ID = 
    SPOTIFY_CLIENT_SECRET = 
    ```

    
4. In `ccny_database_project` folder run: 
    ```bash
    py run.py
    ```