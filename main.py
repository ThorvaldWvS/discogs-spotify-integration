import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

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
        print(f"Error authenticating with Spotify: {e}")
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
    return response.json()

def get_album_tracks(sp, album_id):
    results = sp.album_tracks(album_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

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
    
    try:
        collections = get_discogs_collections(headers, username)
        print("Available collections:")
        for collection in collections['folders']:
            print(f"{collection['id']}: {collection['name']} ({collection['count']} items)")
    except Exception as e:
        print(f"Error fetching Discogs collections: {e}")
        exit(1)

    collection_id = input("Enter the ID of the Discogs collection to scrape: ")
    
    try:
        sp = authenticate_spotify()
        user_id = sp.current_user()['id']
    except Exception as e:
        print(f"Error fetching Spotify user information: {e}")
        exit(1)
    
    try:
        collection = scrape_discogs_collection(headers, collection_id, username)
    except Exception as e:
        print(f"Error fetching Discogs collection: {e}")
        exit(1)
    
    tracks = []
    missing_albums = []
    for item in collection['releases']:
        album_name = item['basic_information']['title']
        artist_name = item['basic_information']['artists'][0]['name']
        print(f"Album: {album_name} by {artist_name}")
        try:
            results = sp.search(q=f"album:{album_name} artist:{artist_name}", type='album')
            if results['albums']['items']:
                album_id = results['albums']['items'][0]['id']
                album_tracks = get_album_tracks(sp, album_id)
                if album_tracks:
                    for track in album_tracks:
                        print(f"  Track: {track['name']}")
                        tracks.append(track['id'])
                else:
                    missing_albums.append(f"{album_name} by {artist_name}")
            else:
                missing_albums.append(f"{album_name} by {artist_name}")
        except Exception as e:
            print(f"Error searching for album '{album_name}' on Spotify: {e}")
            missing_albums.append(f"{album_name} by {artist_name}")
    
    try:
        create_or_update_spotify_playlist(sp, user_id, 'Discogs Collection', tracks)
        print("Playlist created/updated successfully")
    except Exception as e:
        print(f"Error creating/updating Spotify playlist: {e}")

    # Log missing albums to a file
    with open('missing_albums.txt', 'w') as f:
        for album in missing_albums:
            f.write(f"{album}\n")
        print("Missing albums have been logged to missing_albums.txt")

if __name__ == "__main__":
    main()
