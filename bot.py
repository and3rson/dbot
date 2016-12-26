#!/usr/bin/env python2

import settings
import handlers
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    updater = Updater(settings.TOKEN)

    # updater.dispatcher.add_handler(CommandHandler('start', handlers.start))
    # updater.dispatcher.add_handler(MessageHandler(Filters.text, handlers.message))
    # updater.dispatcher.add_handler(CommandHandler('reset', handlers.reset))
    # updater.dispatcher.add_handler(CommandHandler('cancel', handlers.reset))

    updater.job_queue.put(Job(handlers.DotaBuffPollJob(), 30, repeat=True, context=settings.CHAT_ID))

    updater.start_polling()
    updater.idle()
