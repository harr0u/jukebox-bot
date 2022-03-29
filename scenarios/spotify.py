from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from db.user_songs_repository import UserSong, UserSongsRepository
from integration.spotify import SpotifyFacade


def SpotifyLinkScenario(spotifyFacade: SpotifyFacade, user_songs_repository: UserSongsRepository):
    def glue_response(song: UserSong, song_features: dict, spotify_song: str):
        KEYS = ['C', 'C♯ or D', 'D', 'D♯ or E♭', 'E', 'F', 'F♯ or G♭', 'G', 'G♯ or A♭', 'A', 'A or B♭', 'B']

        response = f"{song.song_name} by {song.artist_name}\n\n"
        response += spotify_song['album']['images'][0]['url'] + '\n'

        
        feature_list = ['danceability', 'acousticness', 'energy', ]
        for feature in feature_list:
            response += f"\n{feature.capitalize()} - <b>{int(song.__dict__[feature]*100)}%</b>"


        response += f"\nDepression - <b>{int(song.depression*100)}%</b>"
        response += f"\nTempo - <b>{song.tempo}</b> bpm"
        response += f"\nOverall loudness - <b>{song_features.get('loudness')}</b> dB"
        
        response += f"\nKey - {KEYS[song_features.get('key')]} "
        response += 'Major' if song_features.get('mode') else 'Minor'
        response += f"\nEstimated Time Signature - <b>{song.time_signature}/4</b>"

        if spotifyFacade.is_available_in_russia(spotify_song):
            response += '\n\nTrack is available in russia :('
        else:
            response += '\n\nTrack in not available in russia :)'
        
        response += f'\n<a href="{spotify_song["external_urls"]["spotify"]}">link</a>'

        return response

    def callback(update: Update, context: CallbackContext) -> None:
        spotify_id = update.message.text.split('track/')[-1].split('?')[0]

        # TODO: somewhere else
        spotify_song = spotifyFacade.get_song_by_id(spotify_id)
        song_features: dict = spotifyFacade.get_song_features(spotify_id)

        telegram_id = update.message.from_user.id if update.message.forward_from is None else update.message.forward_from.id
        telegram_name = update.message.from_user.full_name if update.message.forward_from is None else update.message.forward_from.full_name
        song = UserSong.fromRawSpotifyData(spotify_song, song_features, telegram_id, telegram_name)
        user_songs_repository.insert_song(song)

        response = glue_response(song, song_features, spotify_song)
        update.message.reply_text(response, parse_mode=ParseMode.HTML)



    return callback