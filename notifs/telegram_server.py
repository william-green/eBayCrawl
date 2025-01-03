import asyncio
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
#from util.get_abs_path import get_abs_path
from pathlib import Path
from db import db_functions as db_f
from telegram import Bot
import time
import threading

#root directory of project
#path = get_abs_path()

above_root_dir = Path(__file__).resolve().parent.parent.parent


telegram_key_path = above_root_dir / 'eBay_Crawl_keys' / 'telegram_key.txt'
telegram_channel_key_path = above_root_dir / 'eBay_Crawl_keys' / 'telegram_key.txt'

telegram_key = ""
channel_id = ""

def get_telegram_key() -> str:
    try:
        with open(telegram_key_path, "r") as telegram_key_file:
            return telegram_key_file.read()
    except FileNotFoundError:
        print("telegram api key file not found")
    return ""

def get_telegram_channel_id() -> str:
    try:
        with open(telegram_channel_key_path, "r") as telegram_channel_id_file:
            return telegram_channel_id_file.read()
    except FileNotFoundError:
        print("telegram channel id file not found")
    return ""


async def producer_bin_notif(queue: asyncio.PriorityQueue, start_time):
    print("update notification queue")
    while True:
        print("updating notification queue")
        db_notifications = db_f.refresh_bin_notifications()
        for db_notification in db_notifications:
            timestamp = time.time() - start_time
            item = (timestamp, db_notification['url'])
            await queue.put(item)
            #(text=db_notification['url'])
            print("notif")
        await asyncio.sleep(1)

async def consumer_telegram_notif(queue: asyncio.PriorityQueue):
    # Replace with your channel username or ID (start with '@' for username)
    CHANNEL_ID = get_telegram_channel_id()
    bot = Bot(token=get_telegram_key())

    #sender loop. sleep is needed to not exceed telegram rate limit
    while True:
        print("consuming notification queue")
        try:
            item = await queue.get()
            if item is None:
                break
            timestamp, value = item
            await bot.send_message(chat_id=CHANNEL_ID, text=value)
            await asyncio.sleep(3.2)
        except Exception as e:
            print(f"Error from telegram server: {e}")
            await asyncio.sleep(3.2)

def start_loop(queue):
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(queue))

async def main(queue):
    # Start multiple producers and consumers sharing the same queue
    producer1 = asyncio.create_task(producer_bin_notif(queue, time.time()))
    #producer2 = asyncio.create_task(producer(queue, "Producer 2"))
    consumer_task = asyncio.create_task(consumer_telegram_notif(queue))

    # Wait for producers and consumers to finish
    #await asyncio.gather(producer1, producer2)
    await asyncio.gather(producer1)

    # Add a sentinel value to stop the consumer task
    await queue.put(None)
    
    # Wait for the consumer to finish
    await consumer_task

    print("All tasks completed!")


#this is main
def init_telegram_bot():

    # Initialize the shared queue
    queue = asyncio.PriorityQueue()

    # Start the event loop in a separate thread
    thread = threading.Thread(target=start_loop, args=(queue,))
    thread.start()

    print("Main program continues to run...")

    # Wait for the thread to finish
    thread.join()