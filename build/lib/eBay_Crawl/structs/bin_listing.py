

class Bin_listing:
    search_id: int
    ebay_listing_id: int
    url: str
    accepts_best_offer: bool
    price: float
    def __init__(self, search_id: int, ebay_listing_id, url: str, accepts_best_offer: bool, price: float):
        self.search_id = search_id
        self.ebay_listing_id = int(ebay_listing_id)
        self.url = url
        self.accepts_best_offer = accepts_best_offer
        self.price = price

    def get_search_id(self) -> int:
        return self.search_id
    
    def get_ebay_listing_id(self) -> int:
        return self.ebay_listing_id
    
    def get_accepts_best_offer(self) -> bool:
        return self.accepts_best_offer
    
    def get_listing_url(self) -> str:
        return self.url
    
    def get_price(self) -> float:
        return self.price