#!/usr/bin/env python3
"""
Script to convert JSON data from fetch_data_for_youtube_urls.py into SQL insert statements
for the music_content table.
"""

import json
import sys
import sqlite3
from typing import Dict, Any, List
from datetime import datetime

def clean_type(content_type: str) -> str:
    """Convert content type to match schema constraints."""
    type_map = {
        "Album": "ALBUM",
        "Playlist": "PLAYLIST",
        "Video": "SONG",
        "Artist": "ARTIST"
    }
    return type_map.get(content_type, "SONG")  # Default to SONG if unknown

def clean_tags(tags: List[str]) -> str:
    """Convert tags list to a comma-separated string."""
    if not tags:
        return ""
    return ",".join(tag.strip() for tag in tags if tag.strip())

def generate_insert_statements(data: Dict[str, Any]) -> List[str]:
    """Generate SQL insert statements from the JSON data."""
    statements = []
    
    for url, metadata in data.items():
        if "error" in metadata:
            print(f"Skipping {url} due to error: {metadata['error']}", file=sys.stderr)
            continue
            
        # Clean and validate the data
        content_type = clean_type(metadata["type"])
        youtube_id = metadata["youtube_id"]
        name = metadata["name"].replace("'", "''")  # Escape single quotes
        artist_name = metadata.get("artist_name", "").replace("'", "''") if metadata.get("artist_name") else None
        # for now: ignore description and raw tags, the quality is too low.
        # description = metadata.get("description", "").replace("'", "''") if metadata.get("description") else None
        # raw_tags = clean_tags(metadata.get("tags", []))
        description = None
        raw_tags = None

        # Create the insert statement
        statement = f"""INSERT INTO music_content 
            (type, youtube_id, name, artist_name, description, raw_tags)
            VALUES 
            ('{content_type}', '{youtube_id}', '{name}', 
            {f"'{artist_name}'" if artist_name else 'NULL'}, 
            {f"'{description}'" if description else 'NULL'}, 
            {f"'{raw_tags}'" if raw_tags else 'NULL'});"""
            
        statements.append(statement)
    
    return statements

def main():
    if len(sys.argv) != 2:
        print("Usage: python ingest_json_to_table.py <input_json_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
            
        statements = generate_insert_statements(data)
        
        # Print statements to stdout
        for statement in statements:
            print(statement)
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{input_file}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
