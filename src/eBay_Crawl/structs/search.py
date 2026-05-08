

class Search:
    start_url: str
    min_price: float
    max_price: float
    search_type: str
    page_number: int
    id: int
    complete: bool
    #max_pages is the maximum number of search result pages to iterate
    def __init__(self, db_search_dict: dict, max_pages=None):
        self.start_url = db_search_dict['url']
        self.min_price = db_search_dict['min_price']
        self.max_price = db_search_dict['max_price']
        self.search_type = db_search_dict['type']
        self.id = db_search_dict['id']
        self.page_number = 1
        self.complete = False
        self.max_pages = max_pages

    def get_next_page_url(self) -> str:
        #check if search is complete
        if self.complete:
            return ""

        #check whether to mark complete
        if self.max_pages is not None:
            if self.page_number == self.max_pages:
                self.set_complete()
        
        #increment page number and return updated url string
        curr_page_num = self.page_number
        self.page_number += 1
        return self.start_url + "&_pgn=" + str(curr_page_num)
    
    def get_min_price(self) -> float:
        return self.min_price
    
    def get_max_price(self) -> float:
        return self.max_price
    
    def get_search_id(self) -> int:
        return self.id
    
    def get_search_type(self) -> str:
        return self.search_type
    
    def get_complete(self) -> bool:
        return self.complete

    def set_complete(self):
        self.complete = True