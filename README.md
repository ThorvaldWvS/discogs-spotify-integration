# Discogs to Spotify Playlist

This project allows you to scrape your Discogs collection and add the tracks to a Spotify playlist. You can select which collection to scrape using a terminal interface. If the playlist already contains the tracks, it will be updated accordingly.

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/githubnext/workspace-blank.git
    cd workspace-blank
    ```

2. Create a virtual environment and activate it:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required libraries:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up your Discogs and Spotify API credentials:
    - Create a `.env` file in the root directory of the project.
    - Add your Discogs and Spotify API credentials to the `.env` file:
        ```plaintext
        DISCOGS_USER_TOKEN=your_discogs_user_token
        SPOTIPY_CLIENT_ID=your_spotify_client_id
        SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
        SPOTIPY_REDIRECT_URI=your_spotify_redirect_uri
        ```

## Usage

1. Run the main script:
    ```sh
    python main.py
    ```

2. The script will prompt you to enter your Discogs username and list all available collections.

3. Enter the ID of the Discogs collection you want to scrape.

4. The script will print the albums and their tracks in the terminal for verification before adding them to the playlist.

5. Any albums that do not have songs found on Spotify will be logged to `missing_albums.txt` for manual addition later.

6. The tracks from the selected collection will be added to a Spotify playlist. If the playlist already contains the tracks, it will be updated accordingly.
