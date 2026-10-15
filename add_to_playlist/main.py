# /// script
# requires-python = ">=3.11"
# dependencies = ["spotipy>=2.25"]
# ///
import os
import re
import sys
import tomllib
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyPKCE

config_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "spotify-add"
config_file = config_dir / "config.toml"


def setup():
    if not sys.stdin.isatty():
        print("Prima configurazione: esegui lo script da terminale")
        sys.exit(2)
    print("Configurazione iniziale")
    print("Redirect URI da impostare sull'app Spotify: http://127.0.0.1:8888/callback")
    client_id = input("Client ID: ").strip()
    playlist = input("Link o ID della playlist: ").strip()
    match = re.search(r"playlist[/:]([A-Za-z0-9]+)", playlist)
    playlist_id = match.group(1) if match else playlist
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.write_text(f'client_id = "{client_id}"\nplaylist_id = "{playlist_id}"\n')
    config_file.chmod(0o600)
    print(f"Salvato in {config_file}")


if not config_file.exists():
    setup()

config = tomllib.loads(config_file.read_text())
client_id = config.get("client_id")
playlist_id = config.get("playlist_id")
if not client_id or not playlist_id:
    print(f"client_id e playlist_id richiesti in {config_file}")
    sys.exit(2)

sp = spotipy.Spotify(auth_manager=SpotifyPKCE(
    client_id=client_id,
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-read-currently-playing playlist-modify-private playlist-modify-public",
    cache_path=str(config_dir / "token_cache"),
))

cur = sp.current_user_playing_track()
if not cur or not cur.get("item"):
    print("Nessun brano in riproduzione")
    sys.exit(1)

item = cur["item"]
sp.playlist_add_items(playlist_id, [item["uri"]])
print(f'{item["name"]} - {item["artists"][0]["name"]}')