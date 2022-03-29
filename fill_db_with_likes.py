import logging
from config import Config
from integration.spotify import SpotifyFacade
from db.user_songs_repository import UserSong, UserSongsRepository

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def main() -> None:
    config = Config('./config.json')
    spotifyFacade = SpotifyFacade(config.values['client_id'], config.values['client_secret'], "http://localhost:8888/callback")
    user_songs_repository = UserSongsRepository('jukebox.sqlite', logger)

    limit = 25
    total = spotifyFacade.sp.current_user_saved_tracks(limit=1)['total']
    for offset in range(0, total, limit):
        songs = spotifyFacade.sp.current_user_saved_tracks(limit=limit, offset=offset)['items']

        for song in songs:
            song = song['track']
            spotify_id = song['id']

            song_features = spotifyFacade.get_song_features(spotify_id)
            telegram_id = ''

            domain_song = UserSong.fromRawSpotifyData(song, song_features, telegram_id)

            user_songs_repository.insert_song(domain_song, no_commit=True)
        user_songs_repository.connection.commit()



if __name__ == '__main__':
    main()