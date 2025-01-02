from telegram import Bot
from telegram.ext import Application, CommandHandler

#root directory of project
path = "/Users/williamgreen/Documents/GitHub/eBayCrawl/"

telegram_key = ""

def get_telegram_key() -> str:
    try:
        with open(path+"../eBay_Crawl_keys/telegram_key.txt", "r") as telegram_key_file:
            return telegram_key_file.read()
    except FileNotFoundError:
        print("telegram api key not found")
    return ""

async def start(update, context):
    await update.message.reply_text("test bot")

def init_telegram_bot(telegram_key=telegram_key):
    app = Application.builder().token(telegram_key).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

def main():
    telegram_key = get_telegram_key()
    init_telegram_bot(telegram_key)
    #get_chat_ids(telegram_key=telegram_key)

if __name__ == "__main__":
    main()
