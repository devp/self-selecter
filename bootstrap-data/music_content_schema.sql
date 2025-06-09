CREATE TABLE music_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK (type IN ('ALBUM', 'PLAYLIST', 'SONG', 'ARTIST')),
    youtube_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    artist_name TEXT,
    description TEXT,
    raw_tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on type for filtering by content type
CREATE INDEX idx_music_content_created_at ON music_content(created_at);