#from dotenv import load_dotenv
import os

#load_dotenv()

api_key = os.environ.get("Telegram_API_KEY")

if not api_key:
    print("no api key found")
else:
    print(api_key)