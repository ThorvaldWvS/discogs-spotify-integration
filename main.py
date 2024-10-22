import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from tkinter import messagebox
import os
from dotenv import load_dotenv

load_dotenv()

DISCOGS_USER_TOKEN = os.getenv('DISCOGS_USER_TOKEN')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

def authenticate_discogs():
    headers = {
        'Authorization': f'Discogs token={DISCOGS_USER_TOKEN}',
        'User-Agent': 'DiscogsToSpotify/0.1'
    }
    return headers

def authenticate_spotify():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                   client_secret=SPOTIPY_CLIENT_SECRET,
                                                   redirect_uri=SPOTIPY_REDIRECT_URI,
                                                   scope="playlist-modify-public"))
    return sp

def scrape_discogs_collection(headers, collection_id):
    url = f'https://api.discogs.com/users/{collection_id}/collection/folders/0/releases'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception('Error fetching Discogs collection')
    return response.json()

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

    sp.user_playlist_replace_tracks(user_id, playlist_id, tracks)

def create_gui():
    def on_submit():
        collection_id = entry.get()
        if not collection_id:
            messagebox.showerror("Error", "Please enter a collection ID")
            return
        headers = authenticate_discogs()
        sp = authenticate_spotify()
        user_id = sp.current_user()['id']
        collection = scrape_discogs_collection(headers, collection_id)
        tracks = []
        for item in collection['releases']:
            track_name = item['basic_information']['title']
            results = sp.search(q=track_name, type='track')
            if results['tracks']['items']:
                track_id = results['tracks']['items'][0]['id']
                tracks.append(track_id)
        create_or_update_spotify_playlist(sp, user_id, 'Discogs Collection', tracks)
        messagebox.showinfo("Success", "Playlist created/updated successfully")

    root = tk.Tk()
    root.title("Discogs to Spotify Playlist")

    label = tk.Label(root, text="Enter Discogs Collection ID:")
    label.pack(pady=10)

    entry = tk.Entry(root)
    entry.pack(pady=5)

    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.pack(pady=10)

    root.mainloop()

def main():
    create_gui()

if __name__ == "__main__":
    main()
