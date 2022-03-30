import logging

from telegram import Update, MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import Config

from scenarios.spotify import SpotifyLinkScenario
from integration.spotify import SpotifyFacade
from db.user_songs_repository import UserSongsRepository
from filters import SpotifyLinkFilter


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Send spotify link')

def album_image(spotifyFacade: SpotifyFacade):
    def callback(update: Update, context: CallbackContext) -> None:
        album_name = update.message.text
        album = None
        try:
          album = spotifyFacade.searchAlbums(album_name, limit=1)[0]
        except Exception:
          return
        try:
          update.message.reply_text('Take a look at album with similar name\n' + album['images'][0]['url'])
        except Exception:
          return
    return callback


def main() -> None:
    config = Config('config.json')
    updater = Updater(config.values['telegram_token'])
    
    user_songs_repository = UserSongsRepository('jukebox.sqlite', logger)
    spotifyFacade = SpotifyFacade(config.values['client_id'], config.values['client_secret'], "http://localhost:8888/callback")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.entity(MessageEntity.URL) & SpotifyLinkFilter(), SpotifyLinkScenario(spotifyFacade, user_songs_repository)))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
