;; REPL script for interacting with the music database.

;; 1. Require necessary modules
(local lsqlite3 (require :lsqlite3))
;; (macro debug [& args] `(print (text.pretty ...args))) ;; Uncomment for debugging

;; 2. Database Connection
(fn connect-db [?db-path]
  "Establishes a connection to the SQLite database.
   Args:
     ?db-path (string, optional): Path to the SQLite database file.
                                 Defaults to \"../devp/wip-db.sql\".
   Returns:
     A database connection object or nil if connection fails."
  (let [path (or ?db-path "../devp/wip-db.sql")]
    (print (.. "Attempting to connect to database: " path))
    (let [status db (pcall lsqlite3.open path)]
      (if status
          (do
            (print "Successfully connected to database.")
            db)
          (do
            (print (.. "Error connecting to database: " db)) ;; db here is the error message
            nil)))))

;; 3. Data Conversion
(fn sql-row-to-track [row]
  "Converts a SQLite row (table with string keys) to a Fennel track table (keyword keys).
   Args:
     row (table): A table representing a row from the database.
                  Example: {\"id\" 1 \"name\" \"Song Name\" \"artist_name\" \"Artist\" ...}
   Returns:
     A Fennel track table with keyword keys.
     Example: {:id 1 :name \"Song Name\" :artist-name \"Artist\" :type :song ...}"
  (let [track-type (if (. row :type)
                       (keyword (string.lower (. row :type)))
                       :unknown)]
    {;; Core fields from music_content_schema.sql
     :id (. row :id)
     :name (. row :name)
     :artist-name (. row :artist_name)
     :type track-type
     :youtube-id (. row :youtube_id)
     :description (. row :description)
     :raw-tags (. row :raw_tags)
     :created-at (. row :created_at)
     :updated-at (. row :updated_at)
     ;; Additional potential fields from schema (ensure they are handled if present)
     :duration_ms (. row :duration_ms)
     :thumbnail_url (. row :thumbnail_url)
     :playback_count (. row :playback_count)
     :rating (. row :rating)
     :source_info (. row :source_info)
     :local_path (. row :local_path)
     :parent_id (. row :parent_id)
     }))

;; 4. Track Querying
(fn query-tracks [db sql-query ?params]
  "Executes a SQL query and returns a sequence of Fennel track tables.
   Args:
     db (object): The database connection object.
     sql-query (string): The SQL query to execute.
     ?params (sequence, optional): A list of parameters for the SQL query.
   Returns:
     A Fennel sequence (array) of track tables, or nil if an error occurs."
  (let [tracks []
        iter-fn (if ?params
                    (db:nrows sql-query ?params)
                    (db:nrows sql-query))]
    (match (pcall
            (fn []
              (each [row (iter-fn)]
                (table.insert tracks (sql-row-to-track row)))))
      (true _res) tracks ;; pcall returns true and result on success
      (false err) (do
                    (print (.. "Error executing query: " (tostring err)))
                    nil))))

;; 5. Utility/Filtering Functions
(fn get-all-tracks [db ?limit]
  "Fetches all tracks, optionally limited.
   Args:
     db (object): The database connection object.
     ?limit (number, optional): Maximum number of tracks to return.
   Returns:
     A Fennel sequence of track tables."
  (let [base-query "SELECT * FROM music_content"]
    (query-tracks db
                  (if ?limit
                      (.. base-query " LIMIT " (tostring ?limit))
                      base-query))))

(fn get-tracks-by-artist [db artist-name ?limit]
  "Fetches tracks by a specific artist.
   Args:
     db (object): The database connection object.
     artist-name (string): The name of the artist.
     ?limit (number, optional): Maximum number of tracks to return.
   Returns:
     A Fennel sequence of track tables."
  (let [base-query "SELECT * FROM music_content WHERE artist_name = ?"]
    (query-tracks db
                  (if ?limit
                      (.. base-query " LIMIT " (tostring ?limit))
                      base-query)
                  [artist-name])))

(fn get-tracks-by-type [db type-keyword ?limit]
  "Fetches tracks by type (e.g., :song, :album).
   Args:
     db (object): The database connection object.
     type-keyword (keyword): The type of track (e.g., :song).
     ?limit (number, optional): Maximum number of tracks to return.
   Returns:
     A Fennel sequence of track tables."
  (let [type-string (string.upper (tostring type-keyword))]
    (let [base-query "SELECT * FROM music_content WHERE type = ?"]
      (query-tracks db
                    (if ?limit
                        (.. base-query " LIMIT " (tostring ?limit))
                        base-query)
                    [type-string]))))

(fn get-tracks-by-tag [db tag ?limit]
  "Fetches tracks containing a specific tag in raw_tags.
   Args:
     db (object): The database connection object.
     tag (string): The tag to search for.
     ?limit (number, optional): Maximum number of tracks to return.
   Returns:
     A Fennel sequence of track tables."
  (let [base-query "SELECT * FROM music_content WHERE raw_tags LIKE ?"]
    (query-tracks db
                  (if ?limit
                      (.. base-query " LIMIT " (tostring ?limit))
                      base-query)
                  [(.. "%" tag "%")])))

(fn find-track-by-name [db name ?limit]
  "Fetches tracks with a name similar to the input.
   Args:
     db (object): The database connection object.
     name (string): The name (or part of the name) to search for.
     ?limit (number, optional): Maximum number of tracks to return.
   Returns:
     A Fennel sequence of track tables."
  (let [base-query "SELECT * FROM music_content WHERE name LIKE ?"]
    (query-tracks db
                  (if ?limit
                      (.. base-query " LIMIT " (tostring ?limit))
                      base-query)
                  [(.. "%" name "%")])))

;; 6. Pretty Printing
(fn pp-tracks [tracks]
  "Pretty-prints a sequence of tracks to the console.
   Args:
     tracks (sequence): A Fennel sequence of track tables."
  (if (and tracks (> (length tracks) 0))
      (each [i track (ipairs tracks)]
        (print (.. "#" i ": " (. track :name)
                   " - Artist: " (. track :artist-name)
                   " - Type: " (tostring (. track :type))
                   (if (. track :youtube-id) (.. " - YT: " (. track :youtube-id)) "")
                   (if (. track :raw-tags) (.. " - Tags: [" (. track :raw-tags) "]") ""))))
      (print "No tracks to display.")))

;; 7. REPL Environment Setup
(print "--- Fennel Music REPL ---")
(local db (connect-db)) ;; Uses default DB path

(if db
    (print "Database connection established. The 'db' variable is available.")
    (print "Failed to establish database connection. Most functions will not work."))

(print "Available functions include:")
(print "- (connect-db [?db-path])")
(print "- (sql-row-to-track row)")
(print "- (query-tracks db sql-query ?params)")
(print "- (get-all-tracks db ?limit)")
(print "- (get-tracks-by-artist db artist-name ?limit)")
(print "- (get-tracks-by-type db type-keyword ?limit)")
(print "- (get-tracks-by-tag db tag ?limit)")
(print "- (find-track-by-name db name ?limit)")
(print "- (pp-tracks tracks)")
(print "--- Enjoy exploring your music! ---")

;; Make functions available in the global environment for easier REPL use
;; Fennel automatically makes functions defined with `fn` available in the module scope.
;; If this script is loaded with `dofile`, they become global.
;; For a true REPL environment, these would be directly usable.
_G.connect_db = connect-db
_G.sql_row_to_track = sql-row-to-track
_G.query_tracks = query-tracks
_G.get_all_tracks = get-all-tracks
_G.get_tracks_by_artist = get-tracks-by-artist
_G.get_tracks_by_type = get-tracks-by-type
_G.get_tracks_by_tag = get-tracks-by-tag
_G.find_track_by_name = find-track-by-name
_G.pp_tracks = pp-tracks
_G.db = db ;; Also make the default db connection global

;; End of repl.fnl
