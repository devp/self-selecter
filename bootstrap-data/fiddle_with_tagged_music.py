#!/usr/bin/env python3
"""
Script to manage music content in SQLite database.
Commands:
1. add <url> [tags] - Add a URL with optional tags
2. list [--limit N] [--recent] [--untagged] - List content with options
3. tag <id> <tags> - Add tags to an entry by ID
4. play <id> - Open the appropriate YouTube Music URL for the given content ID
"""

import os
import sys
import json
import sqlite3
import subprocess
from typing import List, Optional
from datetime import datetime
from urllib.parse import urlparse

def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Get SQLite database connection."""
    return sqlite3.connect(db_path)

def add_url(db_path: str, url: str, tags: Optional[str] = None) -> None:
    """Add a URL to the database, processing it through the pipeline."""
    # Create temporary files for the pipeline
    temp_input = "temp_urls.txt"
    temp_json = "temp_metadata.json"
    temp_sql = "temp_insert.sql"
    
    try:
        # Write URL to temp file
        with open(temp_input, 'w') as f:
            f.write(url + '\n')
        
        # Run fetch_data_for_youtube_urls.py
        subprocess.run(['python3', 'fetch_data_for_youtube_urls.py', temp_input, temp_json], check=True)
        
        # Read the JSON data
        with open(temp_json, 'r') as f:
            data = json.load(f)
        
        # Get the metadata for our URL
        if url not in data:
            print(f"Error: Could not fetch metadata for {url}")
            return
            
        metadata = data[url]
        if "error" in metadata:
            print(f"Error: {metadata['error']}")
            return
        
        # Add any provided tags
        if tags:
            metadata['tags'] = metadata.get('tags', []) + [tag.strip() for tag in tags.split(',')]
        
        # Write the modified data back to JSON
        with open(temp_json, 'w') as f:
            json.dump({url: metadata}, f)
        
        # Run ingest_json_to_table.py to generate SQL
        with open(temp_sql, 'w') as f:
            subprocess.run(['python3', 'ingest_json_to_table.py', temp_json], stdout=f, check=True)
        
        # Execute the generated SQL
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        with open(temp_sql, 'r') as f:
            sql = f.read()
            cursor.executescript(sql)
        
        conn.commit()
        print(f"Added {metadata['name']} to database")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running pipeline: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up temp files
        for temp_file in [temp_input, temp_json, temp_sql]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

def list_content(db_path: str, limit: int = 20, recent: bool = False, untagged: bool = False) -> None:
    """List content from the database with various options."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Build the query
    query = "SELECT id, type, name, artist_name, raw_tags, created_at FROM music_content"
    conditions = []
    
    if untagged:
        conditions.append("(raw_tags IS NULL OR raw_tags = '')")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    if recent:
        query += " ORDER BY created_at DESC"
    
    query += f" LIMIT {limit}"
    
    # Execute query
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Print results
    if not rows:
        print("No content found")
        return
        
    print("\nID | Type | Name | Artist | Tags | Created At")
    print("-" * 80)
    for row in rows:
        id, type, name, artist, tags, created = row
        print(f"{id} | {type} | {name} | {artist or 'N/A'} | {tags or 'N/A'} | {created}")

def add_tags(db_path: str, id: int, tags: str) -> None:
    """Add tags to an entry by ID."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Get current tags
    cursor.execute("SELECT raw_tags FROM music_content WHERE id = ?", (id,))
    result = cursor.fetchone()
    
    if not result:
        print(f"Error: No entry found with ID {id}")
        return
        
    current_tags = result[0] or ""
    current_tag_list = [tag.strip() for tag in current_tags.split(',')] if current_tags else []
    
    # Add new tags
    new_tags = [tag.strip() for tag in tags.split(',')]
    all_tags = list(set(current_tag_list + new_tags))  # Remove duplicates
    
    # Update the database
    cursor.execute("""
        UPDATE music_content 
        SET raw_tags = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (','.join(all_tags), id))
    
    conn.commit()
    print(f"Updated tags for ID {id}")

def get_youtube_music_url(content_type: str, youtube_id: str) -> str:
    """Construct the appropriate YouTube Music URL based on content type and ID."""
    base_url = "https://music.youtube.com"
    
    if content_type == "ARTIST":
        return f"{base_url}/channel/{youtube_id}"
    elif content_type == "SONG":
        return f"{base_url}/watch?v={youtube_id}"
    else:  # ALBUM or PLAYLIST
        return f"{base_url}/playlist?list={youtube_id}"

def play_content(db_path: str, id: int) -> None:
    """Open the appropriate YouTube Music URL for the given content ID."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Get content type and YouTube ID
    cursor.execute("SELECT type, youtube_id FROM music_content WHERE id = ?", (id,))
    result = cursor.fetchone()
    
    if not result:
        print(f"Error: No entry found with ID {id}")
        return
        
    content_type, youtube_id = result
    url = get_youtube_music_url(content_type, youtube_id)
    
    # Open URL in default browser
    try:
        import webbrowser
        webbrowser.open(url)
        print(f"Opening {url}")
    except Exception as e:
        print(f"Error opening URL: {e}")
        print(f"Please visit: {url}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
        
    command = sys.argv[1]
    db_path = "music.db"  # Default database path
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Database '{db_path}' not found")
        sys.exit(1)

    if command == "add":
        if len(sys.argv) < 3:
            print("Usage: python fiddle_with_tagged_music.py add <url> [tags]")
            sys.exit(1)
        url = sys.argv[2]
        tags = sys.argv[3] if len(sys.argv) > 3 else None
        add_url(db_path, url, tags)
        
    elif command == "list":
        limit = 20
        recent = False
        untagged = False
        
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
                limit = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--recent":
                recent = True
                i += 1
            elif sys.argv[i] == "--untagged":
                untagged = True
                i += 1
            else:
                i += 1
                
        list_content(db_path, limit, recent, untagged)
        
    elif command == "tag":
        if len(sys.argv) < 4:
            print("Usage: python fiddle_with_tagged_music.py tag <id> <tags>")
            sys.exit(1)
        try:
            id = int(sys.argv[2])
            tags = sys.argv[3]
            add_tags(db_path, id, tags)
        except ValueError:
            print("Error: ID must be a number")
            sys.exit(1)
            
    elif command == "play":
        if len(sys.argv) < 3:
            print("Usage: python fiddle_with_tagged_music.py play <id>")
            sys.exit(1)
        try:
            id = int(sys.argv[2])
            play_content(db_path, id)
        except ValueError:
            print("Error: ID must be a number")
            sys.exit(1)
            
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
