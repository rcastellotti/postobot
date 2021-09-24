import threading

import bot
import scraper
from utils import db_cleanup

if __name__ == "__main__":
  scraper.update_bookings()
  threading.Thread(target=scraper.update_bookings_loop).start()
  threading.Thread(target=db_cleanup).start()
  bot.run()
