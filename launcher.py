import os

from bot.bot import Bot
from dotenv import load_dotenv

def main():
    bot = Bot()
    bot.run(token=os.getenv('BOT_TOKEN'))


if __name__ == "__main__":
    load_dotenv()
    main()
