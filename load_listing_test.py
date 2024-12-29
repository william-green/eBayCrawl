import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time

#basic test url
url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=3ds+console&_sacat=0&LH_BIN=1&_sop=10&_ipg=240"

#urls for parallel example
urls = []

def serial_listing_fetch():
    for x in range(12):
        url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=3ds+console&_sacat=0&LH_BIN=1&_sop=10&_ipg=240"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.select(".srp-results")[0].select(".s-item__link")
            #for link in links:
            #    print(link['href'])
        else:
            print("error ", response.status_code)

def fetch_url(url):
    response = requests.get(url)
    return response.text

def parallel_listing_fetch():
    with ThreadPoolExecutor(max_workers=12) as executor:
        #launch parallel request threads
        results = list(executor.map(fetch_url, urls))
        for result in results:
            soup = BeautifulSoup(result, 'html.parser')
            links = soup.select(".srp-results")[0].select(".s-item__link")
            #for link in links:
            #    print(link['href'])

def main():
    serial_start_time = time.time()
    serial_listing_fetch()
    serial_end_time = time.time()
    elapsed_time = serial_end_time - serial_start_time
    print("serial run time: ", str(elapsed_time))

    #build the parallel url list
    for x in range(12):
        urls.append(url)
    parallel_start_time = time.time()
    parallel_listing_fetch()
    parallel_end_time = time.time()
    elapsed_time = parallel_end_time - parallel_start_time
    print("parallel run time: ", elapsed_time)

if __name__ == "__main__":
    main()