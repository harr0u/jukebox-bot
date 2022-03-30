import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyFacade:
    def __init__(self, client_id, client_secret, redirect_uri, scope = "user-library-read") -> None:
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret,
        redirect_uri=redirect_uri, scope=scope))

    def get_song_by_id(self, id: str):
        return self.sp.track(id)

    def get_song_features(self, id: str):
        return self.sp.audio_features([id])[0]

    def searchAlbums(self, q: str, *args, **kwargs):
        limit = kwargs.get('limit', 20)

        try:
          results = self.sp.search(self, q=q, limit=limit, type="album")
          return [album for album in results['albums']['items']]
        except Exception:
          return
    
    def search_songs(self, q: str, *args, **kwargs):
        limit = kwargs.get('limit', 20)

        results = self.sp.search(self, q=q, limit=limit)
        return [track for track in results['tracks']['items']]

    def is_available_in_russia(self, entity):
        return 'RU' in entity['available_markets']
