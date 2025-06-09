"""
Script to fetch metadata from YouTube URLs using the YouTube Data API.
Input: Text file with one YouTube URL per line
Output: JSON file with metadata for each URL
"""

import os
import sys
import json
import re
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

def get_youtube_api_key() -> str:
    """Get YouTube API key from environment variable."""
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set")
        sys.exit(1)
    return api_key

def clean_artist_name(name: str) -> str:
    """Clean artist name by removing YouTube-specific suffixes."""
    if not name:
        return name
    # Remove " - Topic" suffix
    return name.replace(" - Topic", "").strip()

def cap_description(description: str) -> str:
    """Cap description at 80 characters."""
    if not description:
        return description
    return description[:80]

def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from various YouTube URL formats."""
    # Handle youtu.be URLs
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    
    # Handle youtube.com URLs
    parsed_url = urlparse(url)
    if 'youtube.com' in parsed_url.netloc or 'music.youtube.com' in parsed_url.netloc:
        if 'watch' in parsed_url.path:
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif 'playlist' in parsed_url.path:
            return parse_qs(parsed_url.query).get('list', [None])[0]
        elif 'channel' in parsed_url.path:
            return parsed_url.path.split('/')[-1]
    return None

def parse_album_info(title: str, tracks_metadata: List[Dict[str, Any]] = None) -> Tuple[str, str, str]:
    """Parse album title to extract album name and artist name."""
    # First check if this is likely a playlist
    if tracks_metadata:
        # Check if tracks are from different artists
        artists = {track['artist_name'] for track in tracks_metadata if track['artist_name']}
        if len(artists) > 1:
            return "Playlist", title, None
    
    # Remove "Album - " prefix if present
    if title.startswith("Album - "):
        title = title[8:]
        # If it has the Album prefix, it's likely an album
        return "Album", title, None
    
    # Try to extract artist name from the title
    # Common patterns:
    # 1. "Artist - Album Name"
    # 2. "Artist: Album Name"
    # 3. "Artist 'Album Name'"
    artist_name = None
    album_name = title
    
    # Pattern 1: "Artist - Album Name"
    if " - " in title:
        parts = title.split(" - ", 1)
        if len(parts) == 2:
            artist_name = parts[0].strip()
            album_name = parts[1].strip()
            return "Album", album_name, artist_name
    
    # Pattern 2: "Artist: Album Name"
    elif ": " in title:
        parts = title.split(": ", 1)
        if len(parts) == 2:
            artist_name = parts[0].strip()
            album_name = parts[1].strip()
            return "Album", album_name, artist_name
    
    # Pattern 3: "Artist 'Album Name'"
    elif "'" in title:
        parts = title.split("'", 1)
        if len(parts) == 2:
            artist_name = parts[0].strip()
            album_name = parts[1].strip("' ")
            return "Album", album_name, artist_name
    
    # If we get here, it's likely a playlist
    return "Playlist", title, None

def clean_tags(tags: List[str], title: str = None, artist_name: str = None, tracks: List[Dict[str, Any]] = None, is_playlist: bool = False) -> List[str]:
    """Clean tags by removing 'Music', song titles, and artist names."""
    cleaned_tags = set()
    for tag in tags:
        # Skip empty tags
        if not tag or not tag.strip():
            continue
            
        # Skip 'Music' tag
        if tag.lower() == 'music':
            continue
            
        # Skip if tag is the title
        if title and tag.lower() == title.lower():
            continue
            
        # Skip if tag is the artist name (only for playlists)
        if is_playlist and artist_name and tag.lower() == artist_name.lower():
            continue
            
        # Skip if tag matches any track title
        if tracks:
            if any(tag.lower() == track['title'].lower() for track in tracks):
                continue
            
        cleaned_tags.add(tag)
    
    return list(cleaned_tags)

def get_video_metadata(youtube, video_id: str) -> Dict[str, Any]:
    """Fetch metadata for a video using YouTube API."""
    try:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics,topicDetails",
            id=video_id
        )
        response = request.execute()
        
        if not response['items']:
            return {"error": "Video not found"}
            
        video = response['items'][0]
        snippet = video['snippet']
        content_details = video['contentDetails']
        
        # Extract topic categories if available
        topic_categories = []
        if 'topicDetails' in video:
            topic_details = video['topicDetails']
            if 'topicCategories' in topic_details:
                # Extract the last part of the URL which is the category name
                topic_categories = [
                    url.split('/')[-1].replace('_', ' ').title()
                    for url in topic_details['topicCategories']
                ]
        
        # Combine all tags
        tags = set(snippet.get('tags', []))
        tags.update(topic_categories)
        
        # Clean tags
        cleaned_tags = clean_tags(list(tags), snippet['title'], clean_artist_name(snippet.get('channelTitle')))
        
        return {
            "type": "Video",
            "name": snippet['title'],
            "artist_name": clean_artist_name(snippet.get('channelTitle')),
            "youtube_id": video_id,
            "description": cap_description(snippet.get('description')),
            "tags": cleaned_tags
        }
    except HttpError as e:
        return {"error": f"API Error: {str(e)}"}

def get_playlist_tracks_metadata(youtube, playlist_id: str, max_tracks: int = 3) -> List[Dict[str, Any]]:
    """Fetch metadata for the first few tracks in a playlist."""
    try:
        # First get the playlist items
        playlist_items_request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=max_tracks
        )
        playlist_items_response = playlist_items_request.execute()
        
        if not playlist_items_response.get('items'):
            return []
            
        # Get video IDs from playlist items
        video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_items_response['items']]
        
        # Get detailed video information
        videos_request = youtube.videos().list(
            part="snippet,topicDetails",
            id=','.join(video_ids)
        )
        videos_response = videos_request.execute()
        
        tracks_metadata = []
        for video in videos_response.get('items', []):
            snippet = video['snippet']
            
            # Extract topic categories if available
            topic_categories = []
            if 'topicDetails' in video:
                topic_details = video['topicDetails']
                if 'topicCategories' in topic_details:
                    topic_categories = [
                        url.split('/')[-1].replace('_', ' ').title()
                        for url in topic_details['topicCategories']
                    ]
            
            # Combine all tags
            tags = set(snippet.get('tags', []))
            tags.update(topic_categories)
            
            tracks_metadata.append({
                "title": snippet['title'],
                "artist_name": clean_artist_name(snippet.get('channelTitle')),
                "youtube_id": video['id'],
                "description": snippet.get('description'),
                "tags": list(tags)
            })
            
        return tracks_metadata
    except HttpError as e:
        print(f"Error fetching playlist tracks: {str(e)}")
        return []

def get_playlist_metadata(youtube, playlist_id: str) -> Dict[str, Any]:
    """Fetch metadata for a playlist using YouTube API."""
    try:
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            id=playlist_id
        )
        response = request.execute()
        
        if not response['items']:
            return {"error": "Playlist not found"}
            
        playlist = response['items'][0]
        snippet = playlist['snippet']
        
        # Get metadata for first 3 tracks to help with album detection
        tracks_metadata = get_playlist_tracks_metadata(youtube, playlist_id)
        
        # Combine tags from all tracks
        all_tags = set()
        for track in tracks_metadata:
            all_tags.update(track['tags'])
        
        # Check if this is an album
        content_type, name, artist_name = parse_album_info(snippet['title'], tracks_metadata)
        
        # If we couldn't determine the artist from the title, try to get it from the tracks
        if not artist_name and tracks_metadata and content_type == "Album":
            # Look for consistent artist names in tracks
            track_artists = [track['artist_name'] for track in tracks_metadata if track['artist_name']]
            if track_artists and all(artist == track_artists[0] for artist in track_artists):
                artist_name = track_artists[0]
        
        # Clean tags
        cleaned_tags = clean_tags(list(all_tags), name, artist_name, tracks_metadata, is_playlist=True)
        
        return {
            "type": content_type,
            "name": name,
            "artist_name": clean_artist_name(artist_name or snippet.get('channelTitle')),
            "youtube_id": playlist_id,
            "description": cap_description(snippet.get('description')),
            "tags": cleaned_tags
        }
    except HttpError as e:
        return {"error": f"API Error: {str(e)}"}

def get_artist_metadata(youtube, channel_id: str) -> Dict[str, Any]:
    """Fetch metadata for an artist channel using YouTube API."""
    try:
        request = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )
        response = request.execute()
        
        if not response['items']:
            return {"error": "Artist channel not found"}
            
        channel = response['items'][0]
        snippet = channel['snippet']
        
        # Extract topic categories if available
        topic_categories = []
        if 'topicDetails' in channel:
            topic_details = channel['topicDetails']
            if 'topicCategories' in topic_details:
                topic_categories = [
                    url.split('/')[-1].replace('_', ' ').title()
                    for url in topic_details['topicCategories']
                ]
        
        # Combine all tags
        tags = set(snippet.get('tags', []))
        tags.update(topic_categories)
        
        # Clean tags
        cleaned_tags = clean_tags(list(tags), snippet['title'])
        
        # Clean artist name by removing "Topic" suffix
        artist_name = clean_artist_name(snippet['title'])
        
        return {
            "type": "Artist",
            "name": artist_name,
            "youtube_id": channel_id,
            "description": cap_description(snippet.get('description')),
            "tags": cleaned_tags
        }
    except HttpError as e:
        return {"error": f"API Error: {str(e)}"}

def process_urls(input_file: str, output_file: str):
    """Process URLs from input file and save metadata to output file."""
    youtube = build('youtube', 'v3', developerKey=get_youtube_api_key())
    results = {}
    
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    for url in urls:
        video_id = extract_video_id(url)
        if not video_id:
            results[url] = {"error": "Invalid YouTube URL"}
            continue
            
        # Determine if it's a playlist, video, or artist channel
        if 'playlist' in url:
            metadata = get_playlist_metadata(youtube, video_id)
        elif 'channel' in url:
            metadata = get_artist_metadata(youtube, video_id)
        else:
            metadata = get_video_metadata(youtube, video_id)
            
        results[url] = metadata
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

def main():
    if len(sys.argv) != 3:
        print("Usage: python fetch_data_for_youtube_urls.py <input_file> <output_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
        
    process_urls(input_file, output_file)
    print(f"Metadata has been saved to {output_file}")

if __name__ == "__main__":
    main()
