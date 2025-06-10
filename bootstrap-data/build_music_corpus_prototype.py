import sqlite3
import os

DATABASE_NAME = 'music_corpus_prototype.db'
SCHEMA_FILE = 'music_content_schema.sql'
DB_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), SCHEMA_FILE)

def initialize_database():
    """Initializes the SQLite database and creates tables based on the schema file.
    Returns a connection object if successful, None otherwise."""
    conn = None  # Initialize conn to None
    try:
        if not os.path.exists(SCHEMA_PATH):
            print(f"Error: Schema file not found at {SCHEMA_PATH}")
            return None

        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        print(f"Database '{DATABASE_NAME}' initialized successfully with schema from '{SCHEMA_FILE}'.")
        return conn
    except sqlite3.Error as e:
        print(f"SQLite error during database initialization: {e}")
        if conn: # Close connection if it was opened before error
            conn.close()
        return None
    except IOError as e:
        print(f"File error reading schema: {e}")
        if conn: # Should not happen here, but good practice
            conn.close()
        return None

def insert_sample_data(conn):
    """Inserts predefined sample music data into the music_content table."""
    if not conn:
        print("Error: Database connection is not available. Cannot insert data.")
        return

    sample_songs = [
        {
            'type': 'SONG',
            'youtube_id': 'dQw4w9WgXcQ',
            'name': 'Never Gonna Give You Up',
            'artist_name': 'Rick Astley',
            'description': 'Official music video.',
            'raw_tags': 'pop, 80s, classic'
        },
        {
            'type': 'SONG',
            'youtube_id': 'y6120QOlsfU',
            'name': 'Für Elise',
            'artist_name': 'Ludwig van Beethoven',
            'description': 'Classical piano piece.',
            'raw_tags': 'classical, piano, instrumental'
        },
        {
            'type': 'SONG',
            'youtube_id': '3JZ_D3ELwOQ',
            'name': 'Bohemian Rhapsody',
            'artist_name': 'Queen',
            'description': 'Iconic rock opera song.',
            'raw_tags': 'rock, 70s, opera'
        }
    ]

    try:
        cursor = conn.cursor()
        inserted_count = 0
        for song in sample_songs:
            cursor.execute("""
                INSERT OR IGNORE INTO music_content (type, youtube_id, name, artist_name, description, raw_tags)
                VALUES (:type, :youtube_id, :name, :artist_name, :description, :raw_tags)
            """, song)
            if cursor.rowcount > 0:
                inserted_count += 1
        conn.commit()
        if inserted_count > 0:
            print(f"Successfully inserted {inserted_count} new sample songs into the database.")
        else:
            print("Sample songs already exist in the database or no new songs were inserted.")
    except sqlite3.Error as e:
        print(f"SQLite error during data insertion: {e}")
    # No finally conn.close() here, as the connection is managed by the caller (main)

def main():
    """Main function to orchestrate script operations."""
    print("Starting music corpus prototype script...")
    db_conn = initialize_database()

    if db_conn:
        insert_sample_data(db_conn)
        # Clean up: Close the database connection
        db_conn.close()
        print(f"Database connection to '{DATABASE_NAME}' closed.")
    else:
        print("Failed to initialize database. Exiting.")

    print("Music corpus prototype script finished.")

if __name__ == '__main__':
    main()
