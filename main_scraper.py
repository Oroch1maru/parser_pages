import json
import requests

from shop_scraper import ShopScraper

from bs4 import BeautifulSoup
from selenium import webdriver

class MainScraper:
    def __init__(self):
        self.url = "https://www.prospektmaschine.de/hypermarkte/"
        self.driver = webdriver.Chrome()
        self.list_leaflets = []

    def __connect_to_site(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive"
        }

        session = requests.Session()
        session.headers.update(headers)
        return session.get(self.url)

    def __scraper_main_site(self):
        req = self.__connect_to_site()
        soup = BeautifulSoup(req.text, "html.parser")
        list_shop = soup.select(".row.produkt-sidebar-row .box #left-category-shops a")

        base_url = "https://www.prospektmaschine.de"

        for shop in list_shop:
            shop_name = shop.get_text(strip=True)
            shop_url = base_url + shop["href"]
            scraper = ShopScraper(shop_name, shop_url, self.driver)
            leaflets = scraper.scaper()
            if leaflets:
                self.list_leaflets.extend(leaflets)

    def __save_to_json(self, filename="output.json"):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump([leaflet.to_dict() for leaflet in self.list_leaflets], file, ensure_ascii=False, indent=4)

    def run(self):
        self.__scraper_main_site()
        self.__save_to_json()
        self.driver.quit()