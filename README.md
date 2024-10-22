# Discogs to Spotify Playlist

This project allows you to scrape your Discogs collection and add the tracks to a Spotify playlist. You can select which collection to scrape using a graphical user interface (GUI). If the playlist already contains the tracks, it will be updated accordingly.

## Setup

1. Clone the repository:
    ```
    git clone https://github.com/githubnext/workspace-blank.git
    cd workspace-blank
    ```

2. Create a virtual environment and activate it:
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required libraries:
    ```
    pip install -r requirements.txt
    ```

4. Set up your Discogs and Spotify API credentials:
    - Create a `.env` file in the root directory of the project.
    - Add your Discogs and Spotify API credentials to the `.env` file:
        ```
        DISCOGS_USER_TOKEN=your_discogs_user_token
        SPOTIPY_CLIENT_ID=your_spotify_client_id
        SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
        SPOTIPY_REDIRECT_URI=your_spotify_redirect_uri
        ```

## Usage

1. Run the main script:
    ```
    python main.py
    ```

2. A GUI will appear, allowing you to select which Discogs collection to scrape.

3. The tracks from the selected collection will be added to a Spotify playlist. If the playlist already contains the tracks, it will be updated accordingly.
