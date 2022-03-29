from dataclasses import dataclass
from logging import Logger
import sqlite3
from sqlite3 import Error
from sqlite3 import Connection


@dataclass
class UserSong:
    spotify_id: str
    song_name: str
    artist_name: str
    danceability: float
    acousticness : float
    energy: float
    depression: float
    tempo: float
    time_signature: float
    telegram_from: str

    @staticmethod
    def fromRawSpotifyData(song: dict, song_features: dict, telegram_id):
        return UserSong(song['id'], song['name'], ', '.join([a['name'] for a in song['artists']]),
                song_features.get('danceability'), song_features.get('acousticness'), song_features.get('energy'),
                song_features.get('valence'), song_features.get('tempo'), song_features.get('time_signature'),
                telegram_id
        )

class UserSongsRepository:
    def __init__(self, path: str, logger: Logger) -> None:
        self.logger = logger
        self.path = path
        self.setup_connection()

    def setup_connection(self) -> None:
        connection: Connection = None
        try:
            connection = sqlite3.connect(self.path, check_same_thread=False, timeout=10)
            self.logger.log(1, "Connection to SQLite DB successful")
        except Error as e:
            self.logger.error(f"The error '{e}' occurred")

        self.connection = connection

    def try_create_tables(self) -> None:
        cur = self.connection.cursor()

        try:
            cur.execute('''CREATE TABLE songs
                          (spotify_id text, song_name text, artist_name text,
                          danceability real, acousticness real, energy real,
                          depression real, tempo real, time_signature real,
                          telegram_from text,
                          CONSTRAINT songss_pk PRIMARY KEY (spotify_id))''')
            self.connection.commit()
        except:
            self.logger.log(1, 'Tables exists')
        finally:
            cur.close()

    def insert_song(self, song: UserSong, no_commit: bool = False) -> None:
        cur = self.connection.cursor()

        try:
            cur.execute(f'''insert into songs (spotify_id, song_name, artist_name,
                            danceability, acousticness, energy,
                            depression, tempo, time_signature,
                            telegram_from) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            [song.spotify_id, song.song_name,
                            song.artist_name, song.danceability, song.acousticness,
                            song.energy, song.depression, song.tempo, song.time_signature,
                            song.telegram_from])
            if not no_commit:
                self.connection.commit()
        except Exception as e:
            self.logger.error(f'Error with inserting {song.song_name}\n{e}')
        finally:
            cur.close()

