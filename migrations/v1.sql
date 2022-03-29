CREATE TABLE songs(spotify_id text, song_name text, artist_name text, danceability real,
                  acousticness real, energy real, depression real, tempo real,
                  time_signature real, telegram_from text,
                  PRIMARY KEY (spotify_id, telegram_from));

CREATE TABLE jukebox_version(version integer);

INSERT INTO jukebox_version (version) values (1);