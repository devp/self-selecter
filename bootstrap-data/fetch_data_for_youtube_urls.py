"""
TODO: accept a list of youtube URLs, and for each URL:
- validate that it is a youtube URL (and ignore otherwise)
- use the YouTube API to get the music metadata, namely:
- type if Artist, Song, Album, Playlist or Radio
- name (title of song or album, name of artist, etc.)
- artist_name (if belonging to an artist)
- youtube_id (the ID of the youtube video for construction URLs)
- tags (list of tags, genre information, and anything else to help catalog the music)
- misc (any other metadata that might be useful for music curation)

Finally, output the metadata to JSON.
"""

import os
import sys
