# Spotify Artist Remover

This script allows you to remove tracks by a specific artist from all of your Spotify playlists, liked songs and saved albums. It utilizes the Spotify API and requires authentication through OAuth2.

## Features

- Remove tracks by a specific artist from all playlists.
- Remove tracks by a specific artist from liked songs.
- Remove albums by a specific artist from saved albums.

## Setup

1. Install spotipy. `pip install spotipy`

2. Create a Spotify Developer account and register your application to obtain `client_id` and `client_secret`. Set the redirect URI as `http://localhost:8080`.

3. Create a `config.json` file in the same directory as the script with the following format:

```json
{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
}
```

## Usage

Run the script with the artist name as an argument.
With no extra arguments it defaults to playlist removal only.

```bash
python main.py ARTIST_NAME
```

Replace `ARTIST_NAME` with the name of the artist whose tracks you want to remove from your playlists.

> [!NOTE]
If you are using a name with a space anywhere you must pass it using quotes. For example: `"Band Name"`.
The artist name is also case sensitive.

### Options

- `--playlists`: Remove tracks from all playlists (default behavior if no options are provided).
- `--albums`: Remove albums from saved albums.
- `--liked`: Remove tracks from liked songs.

## Notes

- Make sure the artist name matches exactly what's listed in Spotify.
- The script will prompt you to authorize access to your Spotify account the first time you run it. The script does not connect to any external database and is all kept locally on your device. Delete `.cache` if you wish to remove your information.
