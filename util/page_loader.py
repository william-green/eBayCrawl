import requests
from concurrent.futures import ThreadPoolExecutor

import time
import random

def fetch_url(url):
    #early return in case url is blank
    if url == "":
        return ""
    
    #spoofing timing signature
    time.sleep(random.uniform(0, 3))

    response = requests.get(url, timeout=10)
    return response.text

def parallel_page_loader(urls):
    with ThreadPoolExecutor(max_workers=12) as executor:
        #launch parallel request threads
        results = list(executor.map(fetch_url, urls))
        return results