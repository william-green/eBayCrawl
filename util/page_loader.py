import requests
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from requests.exceptions import RequestException

import time
import random

'''
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(RequestException))
def get_with_retry(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise RequestException(f"Request failed with status code {response.status_code}")
    return response
'''

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(RequestException))
def fetch_url(url):
    #early return in case url is blank
    if url == "":
        return ""
    
    #spoofing timing signature
    #time.sleep(random.uniform(0, 3))

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            return ""
    except RequestException as e:
        print(f"Failed to retrieve the page: {e}")
        return ""

def parallel_page_loader(urls):
    with ThreadPoolExecutor(max_workers=12) as executor:
        #launch parallel request threads
        results = list(executor.map(fetch_url, urls))
        return results