from dataclasses import dataclass
from datetime import datetime
from logging import Logger
import sqlite3
import psycopg2
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
    telegram_name: str
    created_at: datetime

    @staticmethod
    def fromRawSpotifyData(song: dict, song_features: dict, telegram_id, telegram_name):
        return UserSong(song['id'], song['name'], ', '.join([a['name'] for a in song['artists']]),
                song_features.get('danceability'), song_features.get('acousticness'), song_features.get('energy'),
                song_features.get('valence'), song_features.get('tempo'), song_features.get('time_signature'),
                telegram_id, telegram_name, datetime.now()
        )

class UserSongsRepository:
    def __init__(self, logger: Logger, **kwargs) -> None:
        pass

    def setup_connection(self, *args, **kwargs) -> None:
        pass
    
    def insert_song(self, song: UserSong, no_commit: bool = False) -> None:
        pass

class UserSongsRepositorySqlite(UserSongsRepository):
    def __init__(self, logger: Logger, **kwargs) -> None:
        self.logger = logger
        self.path = kwargs.get('path', "jukebox.sqlite")
        self.setup_connection()

    def setup_connection(self) -> None:
        connection: Connection = None
        try:
            connection = sqlite3.connect(self.path, check_same_thread=False, timeout=10)
            self.logger.log(1, "Connection to SQLite DB successful")
        except Error as e:
            self.logger.error(f"The error '{e}' occurred")

        self.connection = connection

    def insert_song(self, song: UserSong, no_commit: bool = False) -> None:
        cur = self.connection.cursor()

        try:
            cur.execute(f'''insert into songs (spotify_id, song_name, artist_name,
                            danceability, acousticness, energy,
                            depression, tempo, time_signature,
                            telegram_from, telegram_name, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            [song.spotify_id, song.song_name,
                            song.artist_name, song.danceability, song.acousticness,
                            song.energy, song.depression, song.tempo, song.time_signature,
                            song.telegram_from, song.telegram_name, song.created_at])
            if not no_commit:
                self.connection.commit()
        except Exception as e:
            self.logger.error(f'Error with inserting {song.song_name}\n{e}')
        finally:
            cur.close()

class UserSongsRepositoryPostgres(UserSongsRepository):
    def __init__(self, logger: Logger, **kwargs) -> None:
        self.logger = logger
        self.dbname = kwargs.get('dbname')
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')
        self.host = kwargs.get('host')
        self.port = kwargs.get('port')
        self.setup_connection()

        cursor = self.connection.cursor()
        try:
            migrate(cursor)
        except Exception:
            return

    def setup_psql_connection(self) -> None:
        connection = None
        try:
            connection = psycopg2.connect(dbname=self.dbname, user=self.user,
                password=self.password, host=self.host, port=self.port)
            self.logger.log(1, "Connection to PostgresSQL DB successful")
        except Error as e:
            self.logger.error(f"The error '{e}' occurred")

        self.connection = connection


    def insert_song(self, song: UserSong, no_commit: bool = False) -> None:
        cur = self.connection.cursor()

        try:
            cur.execute(f'''insert into songs (spotify_id, song_name, artist_name,
                            danceability, acousticness, energy,
                            depression, tempo, time_signature,
                            telegram_from, telegram_name, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                            (song.spotify_id, song.song_name,
                            song.artist_name, song.danceability, song.acousticness,
                            song.energy, song.depression, song.tempo, song.time_signature,
                            song.telegram_from, song.telegram_name, song.created_at))
            if not no_commit:
                self.connection.commit()
        except Exception as e:
            self.logger.error(f'Error with inserting {song.song_name}\n{e}')
        finally:
            cur.close()


def migrate(cursor) -> None:
    cursor.execute(
        f'''
        CREATE TABLE songs(spotify_id text, song_name text, artist_name text, danceability real,
              acousticness real, energy real, depression real, tempo real,
              time_signature real, telegram_from text, telegram_name text, 
              created_at DATE,
              PRIMARY KEY (spotify_id, telegram_from));

        CREATE TABLE jukebox_version(version integer);

        INSERT INTO jukebox_version (version) values (3);
          '''
    )