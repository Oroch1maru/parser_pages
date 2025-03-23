import json
import re
from datetime import datetime
import time

from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

start = time.time()


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}


url = "https://www.prospektmaschine.de/hypermarkte/"
session = requests.Session()
session.headers.update(headers)

req = session.get(url)
soup = BeautifulSoup(req.text, "html.parser")

list_shop = soup.select(".row.produkt-sidebar-row .box #left-category-shops a")

url_shop = "https://www.prospektmaschine.de"
list_shop_leaflets=[]

driver = webdriver.Chrome()

now = datetime.now()


for shop in list_shop:
    shop_name = shop.get_text(strip=True)
    # print("-" * 40 + shop_name + "-"*40)

    shop_url = url_shop + shop["href"]
    driver.get(shop_url)

    try:
        wait = WebDriverWait(driver, 10)
        container = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.clearfix.skeleton-loader.done"))
        )
    except:
        print("!!!!Error with loading data!!!!")
        continue
    child_divs = container.find_elements(By.CSS_SELECTOR, "div.brochure-thumb.col-sm-3.col-xs-6")
    for div_car in child_divs:
        description = div_car.find_elements(By.CSS_SELECTOR, ".letak-description p")

        date_element=description[1].find_element(By.CSS_SELECTOR, "small.hidden-sm")
        date=date_element.get_attribute("textContent")

        try:
            start_date, end_date = map(str.strip, date.split("-"))
            parsed_date = datetime.strptime(start_date, "%d.%m.%Y")
            start_date = parsed_date.strftime("%Y-%m-%d")
            parsed_date = datetime.strptime(end_date, "%d.%m.%Y")
            end_date = parsed_date.strftime("%Y-%m-%d")
            if parsed_date.date()<now.date():
                print("continue")
                continue
        except:
            if "von" in date:
                match = re.search(r"\d{2}\.\d{2}\.\d{4}", date)
                if match:
                    start_date = match.group()
                    parsed_date = datetime.strptime(start_date, "%d.%m.%Y")
                    start_date = parsed_date.strftime("%Y-%m-%d")
                    end_date="Until the announcement"
            else:
                start_date="Unidentified"
                end_date="Unidentified"
                print(f"!!!!Error with extracting date: {date}!!!!")

        title=description[0].get_attribute("textContent")
        # print(f"Title: {title}")

        img_tag = div_car.find_element(By.CSS_SELECTOR, "div.img-container img")
        img_src=img_tag.get_attribute("src") or img_tag.get_attribute("data-src")
        # print(f"Image src: {img_src}")

        print(f"Title: {title}")
        print(f"Start date: {start_date}, End date: {end_date}")
        print("-" * 40)

        leaflets={
            "title": title,
            "thumbnail": img_src,
            "shop_name": shop_name,
            "valid_from": start_date,
            "valid_to": end_date,
            "parsed_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        list_shop_leaflets.append(leaflets)
driver.quit()
print(list_shop_leaflets)

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(list_shop_leaflets, f, ensure_ascii=False, indent=4)

end = time.time()
print(f"⏱ Выполнено за {end - start:.2f} секунд")



