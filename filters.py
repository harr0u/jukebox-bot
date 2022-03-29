from telegram.ext import MessageFilter

class SpotifyLinkFilter(MessageFilter):
      def filter(self, message):
          return 'open.spotify' in message.text
