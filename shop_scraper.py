import json
import re

from leaflet import Leaflet
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ShopScraper:
    def __init__(self,shop_name,shop_url,driver):
        self.name = shop_name
        self.url=shop_url
        self.driver=driver
        self.leaflets=[]

    def scaper(self):
        self.driver.get(self.url)
        try:
            wait = WebDriverWait(self.driver, 10)
            container = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.clearfix.skeleton-loader.done"))
            )
        except:
            # print("!!!!Error with loading data!!!!")
            return None

        child_divs = container.find_elements(By.CSS_SELECTOR, "div.brochure-thumb.col-sm-3.col-xs-6")
        for div_car in child_divs:
            description = div_car.find_elements(By.CSS_SELECTOR, ".letak-description p")
            date_element = description[1].find_element(By.CSS_SELECTOR, "small.hidden-sm")
            date_text = date_element.get_attribute("textContent")
            start_date,end_date=self.__parsed_date(date_text)
            if start_date=="Unidentified" and end_date=="Unidentified":
                # print(f"!!!!Error date: {date_text}/ {self.name}!!!!")
                continue
            title = description[0].get_attribute("textContent")
            img_tag = div_car.find_element(By.CSS_SELECTOR, "div.img-container img")
            img_src = img_tag.get_attribute("src") or img_tag.get_attribute("data-src")
            img_src=img_src.split('?')[0]
            self.leaflets.append(Leaflet(title=title,thumbnail=img_src,shop_name=self.name,valid_from=start_date,valid_to=end_date))

        return self.leaflets

    def __parsed_date(selfs,date_text):
        try:
            start_date, end_date = map(str.strip, date_text.split("-"))
            parsed_start_date = datetime.strptime(start_date, "%d.%m.%Y")
            start_date = parsed_start_date.strftime("%Y-%m-%d")
            parsed_end_date = datetime.strptime(end_date, "%d.%m.%Y")
            end_date = parsed_end_date.strftime("%Y-%m-%d")
            if parsed_start_date.date() <= datetime.now().date() <= parsed_end_date.date():
                return start_date,end_date
        except:
            if "von" in date_text:
                match = re.search(r"\d{2}\.\d{2}\.\d{4}", date_text)
                if match:
                    start = datetime.strptime(match.group(), "%d.%m.%Y").strftime("%Y-%m-%d")
                    return start, "Until the announcement"

        return "Unidentified", "Unidentified"