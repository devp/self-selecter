# Music Selection REPL

## Overview

This directory contains a Fennel-based Read-Eval-Print Loop (REPL) for interacting with and querying a music track database. It allows for experimentation with track selection, filtering, and viewing data directly from an SQLite database using Fennel, a Lisp dialect that compiles to Lua.

The primary purpose is to provide a flexible and interactive environment for developers and data curators to explore the music catalog.

## Prerequisites

Before you can use the REPL, you need to have the following dependencies installed:

*   **Fennel**: The Lisp programming language that runs on Lua.
    *   Installation guide: [https://fennel-lang.org/setup](https://fennel-lang.org/setup)
*   **Lua**: Fennel compiles to Lua, so a Lua runtime is required. Lua is often installed as part of the Fennel installation process.
*   **LuaSQLite3**: A Lua module for interacting with SQLite databases.
    *   Typically installed via LuaRocks: `luarocks install lsqlite3`
    *   On some systems, you might need to install SQLite development libraries first (e.g., `sudo apt-get install libsqlite3-dev` on Debian/Ubuntu).

The `run-repl.sh` script includes checks for Fennel and LuaSQLite3 to help you identify if anything is missing.

## Data Format

Tracks and collections of tracks are represented using a homoiconic data format based on Fennel tables (maps) and sequences (arrays). This means the code that represents the data has the same structure as the data itself.

*   Single tracks are Fennel tables with keyword keys (e.g., `:id`, `:name`, `:artist-name`).
*   Collections of tracks are Fennel sequences of these track tables.

For complete details on the data representation, including field descriptions and examples, please see [./data_format.md](./data_format.md).

## Getting Started

1.  **Navigate to the REPL directory**:
    ```bash
    cd path/to/your-repo/bootstrap-data/bootstrap-repl/
    ```

2.  **Make the run script executable** (if you haven't already):
    ```bash
    chmod +x run-repl.sh
    ```

3.  **Launch the REPL**:
    ```bash
    ./run-repl.sh
    ```

Upon successful launch, the script will attempt to connect to an SQLite database located at `../devp/wip-db.sql` (relative to the `bootstrap-data/bootstrap-repl/` directory). A global variable `db` representing this database connection will be available within the REPL.

If the script fails, it will provide error messages indicating missing dependencies or other issues.

## Available Functions

The `repl.fnl` script preloads several functions into the REPL environment for your convenience:

*   `db`: The active SQLite database connection object.
*   `(connect-db ?path)`: Establishes a new database connection. If `?path` is provided, it connects to that database file; otherwise, it uses the default.
*   `(query-tracks db sql-string ?params)`: Executes a raw SQL query. `?params` is an optional sequence of parameters for prepared statements.
*   `(get-all-tracks db ?limit)`: Fetches all tracks, optionally limited by `?limit`.
*   `(get-tracks-by-artist db artist-name ?limit)`: Fetches tracks by a specific artist.
*   `(get-tracks-by-type db type-keyword ?limit)`: Fetches tracks by type (e.g., `:song`, `:album`, `:playlist`).
*   `(get-tracks-by-tag db tag ?limit)`: Fetches tracks containing a specific tag in their `raw_tags` field (case-insensitive partial match).
*   `(find-track-by-name db name ?limit)`: Fetches tracks with a name similar to the input (case-insensitive partial match).
*   `(pp-tracks tracks-seq)`: Pretty-prints a sequence of track tables to the console in a readable format.

**Usage Examples:**

```fennel
;; List the first 5 tracks in the database
(pp-tracks (get-all-tracks db 5))

;; Get all tracks by "Artist Name"
(pp-tracks (get-tracks-by-artist db "Artist Name"))

;; Get up to 10 tracks tagged with "rock"
(pp-tracks (get-tracks-by-tag db "rock" 10))

;; Get all albums
(pp-tracks (get-tracks-by-type db :album))

;; Find tracks with "love" in their name
(pp-tracks (find-track-by-name db "love"))

;; Example of a custom query: Get up to 5 albums by artists containing "Various"
(pp-tracks (query-tracks db "SELECT * FROM music_content WHERE type = 'ALBUM' AND artist_name LIKE ? LIMIT ?" ["%Various%" 5]))

;; To exit the REPL, type (quit) or press Ctrl+D
(quit)
```

## Database Schema

The REPL interacts with the `music_content` table in the SQLite database. Key columns in this table include:

*   `id` (TEXT or INTEGER, Primary Key): Unique identifier.
*   `type` (TEXT): Type of content (e.g., "SONG", "ALBUM", "PLAYLIST").
*   `name` (TEXT): Title of the track/album/playlist.
*   `artist_name` (TEXT): Name of the artist.
*   `raw_tags` (TEXT): Space-separated list of tags.
*   `youtube_id` (TEXT): YouTube video ID.
*   `created_at` (TEXT): ISO 8601 timestamp.
*   `updated_at` (TEXT): ISO 8601 timestamp.

For the complete and detailed schema definition, please refer to the `music_content_schema.sql` file located at [../../music_content_schema.sql](../../music_content_schema.sql).

## Contributing/Extending

You can extend the functionality of this REPL by modifying the `repl.fnl` script. Add new functions, change existing ones, or experiment with different ways to query and present the music data.
The `sql-row-to-track` function in `repl.fnl` handles the mapping from database rows to the Fennel track format.
