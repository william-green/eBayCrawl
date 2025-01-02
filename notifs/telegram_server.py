import asyncio
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from util.get_abs_path import get_abs_path
from db import db_functions as db_f
import time
from telegram import Bot

#root directory of project
path = get_abs_path()

telegram_key = ""

def get_telegram_key() -> str:
    try:
        with open(path+"../eBay_Crawl_keys/telegram_key.txt", "r") as telegram_key_file:
            return telegram_key_file.read()
    except FileNotFoundError:
        print("telegram api key not found")
    return ""

async def run_telegram_bot():
    # Replace with your channel username or ID (start with '@' for username)
    CHANNEL_ID = "-1002412636556"
    bot = Bot(token=get_telegram_key())

    while True:
        await bot.send_message(chat_id=CHANNEL_ID, text="testing")
        time.sleep(3.2)

if __name__ == "__main__":
    asyncio.run(run_telegram_bot())
    print("main")
    #send_message_to_channel("Hello, Channel! This is a message from the bot.")




"""from telegram.ext import Application, CommandHandler, ContextTypes
from util.get_abs_path import get_abs_path
from db import db_functions as db_f
import time

#root directory of project
path = get_abs_path()

telegram_key = ""

def check_bin_notifications_poll(context: ContextTypes.DEFAULT_TYPE):
    while True:
        db_notifications = db_f.refresh_bin_notifications()
        for db_notification in db_notifications:
            context.bot.send_message(text=db_notification['url'])
            print("notif")
        time.sleep(1)

async def send_telegram_message(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(job.context, text="this is a test")


def get_telegram_key() -> str:
    try:
        with open(path+"../eBay_Crawl_keys/telegram_key.txt", "r") as telegram_key_file:
            return telegram_key_file.read()
    except FileNotFoundError:
        print("telegram api key not found")
    return ""

async def start(update, context):
    await update.message.reply_text("test bot")

def init_telegram_bot():
    telegram_key = get_telegram_key()
    app = Application.builder().token(telegram_key).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
    check_bin_notifications_poll()

def main():
    print("main")
    #telegram_key = get_telegram_key()
    #init_telegram_bot(telegram_key)
    #get_chat_ids(telegram_key=telegram_key)

if __name__ == "__main__":
    main()
"""