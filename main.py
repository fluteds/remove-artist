import json
import logging
import spotipy
import sys
from spotipy.oauth2 import SpotifyOAuth

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load Spotify credentials from config.json
with open('config.json') as config_file:
    config = json.load(config_file)
    client_id = config['client_id']
    client_secret = config['client_secret']

# Authenticate with Spotify
scope = "playlist-modify-private playlist-read-private user-library-read user-library-modify"  # Added user-library-read and user-library-modify scopes
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri='http://localhost:8080',
                                               scope=scope))

def remove_artist_from_playlist(artist_name, playlist_id, playlist_name):
    tracks_to_remove = []
    # Get tracks from playlist
    results = sp.playlist_tracks(playlist_id)
    tracks = results.get('items', [])
    if not tracks:
        logging.warning(f"No tracks found in the playlist '{playlist_name}' with ID: {playlist_id}")
        return

    # Find tracks by the specified artist
    for track in tracks:
        if not track or not track.get('track'):
            continue
        for artist in track['track']['artists']:
            if artist['name'] == artist_name:
                tracks_to_remove.append(track['track']['id'])

    # Remove tracks from playlist
    if tracks_to_remove:
        sp.playlist_remove_all_occurrences_of_items(playlist_id, tracks_to_remove)
        logging.info(f"Removed {len(tracks_to_remove)} tracks by {artist_name} from the playlist '{playlist_name}'.")
    else:
        logging.info(f"No tracks by {artist_name} found in the playlist '{playlist_name}'.")

def remove_artist_from_saved_tracks(artist_name):
    results = sp.current_user_saved_tracks()
    tracks = [item['track'] for item in results['items']]
    tracks_to_remove = [track['id'] for track in tracks if any(artist['name'] == artist_name for artist in track['artists'])]
    if tracks_to_remove:
        sp.current_user_saved_tracks_delete(tracks=tracks_to_remove)
        logging.info(f"Removed {len(tracks_to_remove)} tracks by {artist_name} from saved tracks.")
    else:
        logging.info(f"No tracks by {artist_name} found in saved tracks.")

def remove_artist_from_all_playlists_and_saved(artist_name, remove_from_playlists=True, remove_from_albums=False, remove_from_liked=False):
    if remove_from_playlists:
        # Remove from playlists
        playlists = sp.current_user_playlists()
        for playlist in playlists['items']:
            playlist_id = playlist['id']
            playlist_name = playlist['name']
            logging.info(f"Processing playlist '{playlist_name}' with ID: {playlist_id}")
            remove_artist_from_playlist(artist_name, playlist_id, playlist_name)
    
    if remove_from_albums:
        # Remove from saved albums
        results = sp.current_user_saved_albums()
        albums = [album['album']['id'] for album in results['items'] if any(artist['name'] == artist_name for artist in album['album']['artists'])]
        if albums:
            sp.current_user_saved_albums_delete(albums=albums)
            logging.info(f"Removed {len(albums)} albums by {artist_name} from saved albums.")
        else:
            logging.info(f"No albums by {artist_name} found in saved albums.")
        
    if remove_from_liked:
        # Remove from liked tracks
        remove_artist_from_saved_tracks(artist_name)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py ARTIST_NAME [--playlists] [--albums] [--liked]")
        sys.exit(1)
    
    artist_name = sys.argv[1]
    remove_from_playlists = "--playlists" in sys.argv
    remove_from_albums = "--albums" in sys.argv
    remove_from_liked = "--liked" in sys.argv

    if not (remove_from_playlists or remove_from_albums or remove_from_liked):
        remove_from_playlists = True  # Default to removal from playlists if no option is provided

    logging.info(f"Removing tracks by {artist_name} from selected locations...")
    remove_artist_from_all_playlists_and_saved(artist_name, remove_from_playlists, remove_from_albums, remove_from_liked)
