# Data Format for Tracks and Collections

This document defines the homoiconic data format used for representing single tracks and collections of tracks within the system. The chosen representation is Fennel, leveraging its tables (maps) and sequences (arrays).

## Single Track Representation

A single track is represented as a Fennel table (map). The keys of this table are keywords, providing a clear and consistent structure.

**Fields:**

*   `:id` (String): A unique identifier for the track.
*   `:name` (String): The name or title of the track.
*   `:artist-name` (String): The name of the artist associated with the track.
*   `:type` (Keyword): The type of the track. Possible values include:
    *   `:song`
    *   `:album`
    *   `:playlist`
    *   `:artist` (representing a collection of tracks by a specific artist)
*   `:youtube-id` (String, Optional): The YouTube video ID if the track is associated with a YouTube video.
*   `:description` (String, Optional): A textual description of the track.
*   `:raw-tags` (String, Optional): A string containing space-separated tags.
*   `:created-at` (String): Timestamp in ISO 8601 format (e.g., "YYYY-MM-DDTHH:MM:SSZ") indicating when the track record was created.
*   `:updated-at` (String): Timestamp in ISO 8601 format (e.g., "YYYY-MM-DDTHH:MM:SSZ") indicating when the track record was last updated.

**Example of a Single Track:**

```fennel
{
 :id "track-001"
 :name "Example Song Title"
 :artist-name "Artist Name"
 :type :song
 :youtube-id "dQw4w9WgXcQ"
 :description "An example song to demonstrate the data format."
 :raw-tags "example pop instrumental"
 :created-at "2023-10-26T10:00:00Z"
 :updated-at "2023-10-27T14:30:00Z"
}
```

## Collection of Tracks Representation

A collection of tracks is represented as a Fennel sequence (array). Each element in the sequence is a track table, as defined above.

**Example of a Collection of Tracks:**

```fennel
[
 {
  :id "track-001"
  :name "Example Song Title 1"
  :artist-name "Artist Name A"
  :type :song
  :youtube-id "dQw4w9WgXcQ"
  :description "First example song."
  :raw-tags "example pop"
  :created-at "2023-10-26T10:00:00Z"
  :updated-at "2023-10-27T14:30:00Z"
 }
 {
  :id "track-002"
  :name "Another Example Album"
  :artist-name "Artist Name B"
  :type :album
  :description "An example album collection."
  :raw-tags "example album collection rock"
  :created-at "2023-11-01T12:00:00Z"
  :updated-at "2023-11-01T12:00:00Z"
 }
 {
  :id "track-003"
  :name "My Favorite Playlist"
  :artist-name "Various Artists"
  :type :playlist
  :description "A curated playlist of favorite tracks."
  :raw-tags "playlist favorites mixed-genre"
  :created-at "2023-09-15T08:20:00Z"
  :updated-at "2023-10-28T11:45:00Z"
 }
]
```

This data format is designed to be easily readable and writable by both humans and machines, fitting the homoiconic principles of Fennel.
