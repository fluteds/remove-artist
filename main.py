import json
import logging
import spotipy
import sys
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def load_spotify_credentials(file_path='config.json'):
    """Load Spotify credentials from config.json"""
    try:
        with open(file_path) as config_file:
            config = json.load(config_file)
            client_id = config['client_id']
            client_secret = config['client_secret']
            return client_id, client_secret
    except FileNotFoundError:
        logging.error("config.json file not found.")
        sys.exit(1)
    except KeyError as e:
        logging.error(f"Key error: {e}")
        sys.exit(1)

def authenticate_spotify(client_id, client_secret):
    """Authenticate with Spotify"""
    scope = "playlist-modify-public playlist-modify-private playlist-read-private user-library-read user-library-modify"
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                       client_secret=client_secret,
                                                       redirect_uri='http://localhost:8080',
                                                       scope=scope))
        return sp
    except SpotifyException as e:
        logging.error(f"Spotify authentication failed: {e}")
        sys.exit(1)

def remove_artist_from_playlist(sp, artist_name, playlist_id, playlist_name):
    """Remove artist from a playlist"""
    logging.info(f"Processing playlist '{playlist_name}' with ID: {playlist_id}")
    try:
        results = sp.playlist_tracks(playlist_id)
        tracks = results.get('items', [])
        if not tracks:
            logging.warning(f"No tracks found in the playlist '{playlist_name}' with ID: {playlist_id}")
            return

        tracks_to_remove = [track['track']['id'] for track in tracks if track.get('track') and any(artist['name'] == artist_name for artist in track['track']['artists'])]

        if tracks_to_remove:
            sp.playlist_remove_all_occurrences_of_items(playlist_id, tracks_to_remove)
            logging.info(f"Removed {len(tracks_to_remove)} tracks by {artist_name} from the playlist '{playlist_name}'.")
        else:
            logging.info(f"No tracks by {artist_name} found in the playlist '{playlist_name}'.")
    except SpotifyException as e:
        logging.error(f"Error while removing tracks from playlist: {e}")

def remove_artist_from_liked_tracks(sp, artist_name):
    """Remove artist from liked tracks"""
    logging.info("Processing saved tracks...")
    try:
        results = sp.current_user_saved_tracks()
        tracks = [item['track'] for item in results['items']]
        tracks_to_remove = [track['id'] for track in tracks if any(artist['name'] == artist_name for artist in track['artists'])]
        
        if tracks_to_remove:
            sp.current_user_saved_tracks_delete(tracks=tracks_to_remove)
            logging.info(f"Removed {len(tracks_to_remove)} tracks by {artist_name} from saved tracks.")
        else:
            logging.info(f"No tracks by {artist_name} found in saved tracks.")
    except SpotifyException as e:
        logging.error(f"Error while removing tracks from saved tracks: {e}")

def remove_artist_from_all_locations(sp, artist_name, remove_from_playlists=True, remove_from_albums=False, remove_from_liked=False):
    """Remove artist from all locations"""
    logging.info(f"Removing tracks by {artist_name} from selected locations...")
    try:
        if remove_from_playlists:
            playlists = sp.current_user_playlists()
            for playlist in playlists['items']:
                playlist_id = playlist['id']
                playlist_name = playlist['name']
                remove_artist_from_playlist(sp, artist_name, playlist_id, playlist_name)

        if remove_from_albums:
            results = sp.current_user_saved_albums()
            albums = [album['album']['id'] for album in results['items'] if any(artist['name'] == artist_name for artist in album['album']['artists'])]
            if albums:
                sp.current_user_saved_albums_delete(albums=albums)
                logging.info(f"Removed {len(albums)} albums by {artist_name} from saved albums.")
            else:
                logging.info(f"No albums by {artist_name} found in saved albums.")

        if remove_from_liked:
            remove_artist_from_liked_tracks(sp, artist_name)
    except SpotifyException as e:
        logging.error(f"Error while removing tracks: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py ARTIST_NAME [--playlists] [--albums] [--liked]")
        sys.exit(1)

    artist_name = sys.argv[1]
    remove_from_playlists = "--playlists" in sys.argv
    remove_from_albums = "--albums" in sys.argv
    remove_from_liked = "--liked" in sys.argv

    if not (remove_from_playlists or remove_from_albums or remove_from_liked):
        remove_from_playlists = True

    client_id, client_secret = load_spotify_credentials()
    sp = authenticate_spotify(client_id, client_secret)

    remove_artist_from_all_locations(sp, artist_name, remove_from_playlists, remove_from_albums, remove_from_liked)
