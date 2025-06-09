PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
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
INSERT INTO music_content VALUES(11,'ALBUM','OLAK5uy_k8wTaR4CFRnHz2bgBFlQnvXEgo4LD_Q08','Bottom of the Pomps','The Pomps',NULL,'ska','2025-06-09 03:21:00','2025-06-09 03:43:04');
INSERT INTO music_content VALUES(12,'ALBUM','OLAK5uy_ljvbmQkkMF5gjQ2wb0_-85L8nMIOQUUsA','Moonflower','Flying Raccoon Suit',NULL,'ska','2025-06-09 03:21:00','2025-06-09 03:43:04');
INSERT INTO music_content VALUES(13,'PLAYLIST','RDCLAK5uy_l4rPvz8nCpkqPnBxstuE6OhDSRsCW4aVk','nuGaze','YouTube',NULL,'sad,chill','2025-06-09 03:21:00','2025-06-09 03:43:22');
INSERT INTO music_content VALUES(14,'PLAYLIST','RDCLAK5uy_m6aBO70zO2mNRnBrz9vLCLyjMf8hsZKeE','Jazz Coffee Shop','YouTube',NULL,'chill','2025-06-09 03:21:00','2025-06-09 03:43:17');
INSERT INTO music_content VALUES(15,'PLAYLIST','RDCLAK5uy_mdjVozbYlOQr9P4SuS6nHyK2D-k1jxaIY','Presenting Khruangbin','YouTube',NULL,'vibes','2025-06-09 03:21:00','2025-06-09 03:43:43');
INSERT INTO music_content VALUES(16,'ALBUM','OLAK5uy_kqYY6Y7uhh4hAZr23qQiUsgANfiWMeCYo','The Father of Make Believe','Coheed And Cambria',NULL,'nostalgia,rock','2025-06-09 03:21:00','2025-06-09 03:29:21');
INSERT INTO music_content VALUES(17,'SONG','JGJPVl7iQUM','Clair de Lune (Studio Version)','Johann Debussy',NULL,'chill,sleep','2025-06-09 03:21:00','2025-06-09 03:43:49');
INSERT INTO music_content VALUES(18,'SONG','D13U7vFssY4','Sinking Boat','Infinity Song',NULL,'chaos,chill','2025-06-09 03:21:00','2025-06-09 03:44:25');
INSERT INTO music_content VALUES(19,'PLAYLIST','PL0Sds77LYSQSf5-Eaal0HcUKaVRxLVXIw','2025 sucks','Dev Purkayastha',NULL,'chaos','2025-06-09 03:21:00','2025-06-09 03:44:25');
INSERT INTO music_content VALUES(20,'ARTIST','UCPF30lykfqyx7h5NOCvatQw','Rebecca Black',NULL,NULL,'chaos','2025-06-09 03:21:00','2025-06-09 03:42:35');
INSERT INTO music_content VALUES(21,'SONG','3Pt0V6K7WpM','Feel It All Around','Washed Out',NULL,'sad,chill','2025-06-09 03:33:03','2025-06-09 03:43:22');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('music_content',21);
CREATE INDEX idx_music_content_created_at ON music_content(created_at);
COMMIT;
