import os
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Authenticate
auth_manager = SpotifyOAuth(
    scope=[
        "playlist-read-private",
        "playlist-modify-private",
    ],
    open_browser=False,
)

sp = spotipy.Spotify(auth=os.environ["SPOTIFY_ACCESS_TOKEN"], auth_manager=auth_manager)
auth_manager.refresh_access_token(os.environ["SPOTIFY_REFRESH_TOKEN"])


# Get discover weekly playlist
DISCOVER_WEEKLY_PLAYLIST_ID = os.environ["DISCOVER_WEEKLY_PLAYLIST_ID"]
discover_weekly_playlist = sp.playlist(DISCOVER_WEEKLY_PLAYLIST_ID)

# Get original Daily Drive playlist
DAILY_DRIVE_PLAYLIST_ID = os.environ["DAILY_DRIVE_PLAYLIST_ID"]
daily_drive_playlist = sp.playlist(DAILY_DRIVE_PLAYLIST_ID)

# Transform to create new playlist
daily_lowdown_id = 11
ft_pod_id = 21
spoticron_playlist = [track for track in daily_drive_playlist["tracks"]["items"]]

ft_pod = spoticron_playlist.pop(ft_pod_id)
spoticron_playlist.pop(daily_lowdown_id)
spoticron_playlist.insert(daily_lowdown_id, ft_pod)

podcast_ids = [0, 1, 6, 11, 16]
n_to_sample = len(spoticron_playlist) - len(podcast_ids)

new_tracks = random.sample(discover_weekly_playlist["tracks"]["items"], n_to_sample)

for i, track in enumerate(spoticron_playlist):
    if i not in podcast_ids:  # Skip podcasts
        # Replace track with random sample (without replacement) from discover weekly
        spoticron_playlist[i] = new_tracks.pop(0)
    # print(f"{i} 🎧: {track['track']['name']}")

# Write spoticron playlist
print("Spoticron playlist:")
[
    print(f"{i} 🎧: {track['track']['artists'][0]['name']} - {track['track']['name']}")
    for i, track in enumerate(spoticron_playlist)
]

# Empty spoticron playlist
SPOTICRON_PLAYLIST_ID = os.environ["SPOTICRON_PLAYLIST_ID"]
sp.playlist_remove_all_occurrences_of_items(
    SPOTICRON_PLAYLIST_ID,
    [x["track"]["uri"] for x in sp.playlist(SPOTICRON_PLAYLIST_ID)["tracks"]["items"]],
)


# Assert spoticron playlist is empty
assert len(sp.playlist_items(SPOTICRON_PLAYLIST_ID)["items"]) == 0

sp.playlist_add_items(
    SPOTICRON_PLAYLIST_ID,
    [x["track"]["uri"] for x in spoticron_playlist],
)
