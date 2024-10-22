import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import logging

# Load environment variables from the specified .env file
load_dotenv(dotenv_path='credentials.env')

DISCOGS_USER_TOKEN = os.getenv('DISCOGS_USER_TOKEN')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

print(f"DISCOGS_USER_TOKEN: {DISCOGS_USER_TOKEN}")
print(f"SPOTIPY_CLIENT_ID: {SPOTIPY_CLIENT_ID}")
print(f"SPOTIPY_CLIENT_SECRET: {SPOTIPY_CLIENT_SECRET}")
print(f"SPOTIPY_REDIRECT_URI: {SPOTIPY_REDIRECT_URI}")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def authenticate_discogs():
    headers = {
        'Authorization': f'Discogs token={DISCOGS_USER_TOKEN}',
        'User-Agent': 'DiscogsToSpotify/0.1'
    }
    return headers

def authenticate_spotify():
    try:
        sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                client_secret=SPOTIPY_CLIENT_SECRET,
                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                scope="playlist-modify-public")
        auth_url = sp_oauth.get_authorize_url()
        print(f"Please navigate to the following URL to authorize the application: {auth_url}")
        response = input("Enter the URL you were redirected to: ")
        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)
        sp = spotipy.Spotify(auth=token_info['access_token'])
        return sp
    except Exception as e:
        logging.error(f"Error authenticating with Spotify: {e}")
        exit(1)

def get_discogs_collections(headers, username):
    url = f'https://api.discogs.com/users/{username}/collection/folders'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception('Error fetching Discogs collections')
    return response.json()

def scrape_discogs_collection(headers, collection_id, username):
    url = f'https://api.discogs.com/users/{username}/collection/folders/{collection_id}/releases'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception('Error fetching Discogs collection')
    
    collection = response.json()
    tracks = []
    for item in collection['releases']:
        album_id = item['id']
        album_url = f'https://api.discogs.com/releases/{album_id}'
        album_response = requests.get(album_url, headers=headers)
        if album_response.status_code != 200:
            continue
        album_data = album_response.json()
        for track in album_data['tracklist']:
            tracks.append({
                'title': track['title'],
                'artist': item['basic_information']['artists'][0]['name']
            })
        logging.info(f"Scraped album: {item['basic_information']['title']} by {item['basic_information']['artists'][0]['name']}")
    return tracks

def search_spotify_track(sp, track_title, artist_name):
    query = f"track:{track_title} artist:{artist_name}"
    results = sp.search(q=query, type='track')
    if results['tracks']['items']:
        return results['tracks']['items'][0]['id']
    return None

def create_or_update_spotify_playlist(sp, user_id, playlist_name, tracks):
    playlists = sp.user_playlists(user_id)
    playlist_id = None
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            playlist_id = playlist['id']
            break
    if playlist_id is None:
        playlist = sp.user_playlist_create(user_id, playlist_name)
        playlist_id = playlist['id']
    
    # Spotify API limit is 100 tracks per request
    batch_size = 100
    for i in range(0, len(tracks), batch_size):
        sp.user_playlist_add_tracks(user_id, playlist_id, tracks[i:i+batch_size])

def main():
    username = input("Enter your Discogs username: ")
    headers = authenticate_discogs()
    sp = authenticate_spotify()
    
    collections = get_discogs_collections(headers, username)
    
    print("Available collections:")
    for collection in collections['folders']:
        print(f"{collection['id']}: {collection['name']}")
    
    collection_id = input("Enter the ID of the collection to scrape: ")
    logging.info(f"Selected collection ID: {collection_id}")
    
    discogs_tracks = scrape_discogs_collection(headers, collection_id, username)
    logging.info(f"Total tracks scraped from Discogs: {len(discogs_tracks)}")
    
    spotify_tracks = []
    for track in discogs_tracks:
        track_id = search_spotify_track(sp, track['title'], track['artist'])
        if track_id:
            spotify_tracks.append(track_id)
        logging.info(f"Processed track: {track['title']} by {track['artist']}")
    
    user_id = sp.current_user()['id']
    playlist_name = input("Enter the name of the Spotify playlist: ")
    create_or_update_spotify_playlist(sp, user_id, playlist_name, spotify_tracks)
    logging.info(f"Playlist '{playlist_name}' updated with {len(spotify_tracks)} tracks")

if __name__ == "__main__":
    main()
