from telegram.ext import Application, CommandHandler
from pathlib import Path
import os

# Root directory of the repo (tests/ -> repo root)
REPO_ROOT = Path(__file__).resolve().parents[1]
TELEGRAM_KEY_PATH = REPO_ROOT / "eBay_Crawl_keys" / "telegram_key.txt"

telegram_key = ""

def get_telegram_key() -> str:
    # Prefer env var in CI/local automation; fall back to a local file if present.
    api_key = os.environ.get("Telegram_API_KEY")
    if api_key:
        return api_key

    try:
        return TELEGRAM_KEY_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        # Avoid failing test collection when keys are not present in CI.
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
