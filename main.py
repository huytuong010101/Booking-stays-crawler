from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import json

options = webdriver.ChromeOptions()
# options.add_argument("headless")
driver = webdriver.Chrome(options=options)
driver.get(r"https://www.booking.com/index.vi.html?")

# Data store
data = []
# Search
elem = driver.find_element(By.NAME, "ss")
elem.clear()
elem.send_keys("Da Nang, Viet Nam")
elem.send_keys(Keys.RETURN)
has_next = True
page_number = 0
# Now loop all page
while has_next:
    page_number += 1
    print(f">> Now we on page {page_number}")
    # ========================= Crawl data in current page =======================
    # Loop all item in page
    for link in driver.find_elements(By.XPATH, "//a[@data-testid='title-link']"):
        # Item data
        item = {}
        # Open item in new tab
        link.click()
        sleep(1)
        driver.switch_to.window(driver.window_handles[-1])
        # =========== Crawling in new tab =============
        title = driver.find_element(By.ID, "hp_hotel_name").text
        hotel_name = title.split("\n")[-1]
        stay_type = title.split("\n")[0]
        try:
            address_longlat = driver.find_element(By.ID, "hotel_header").get_attribute("data-atlas-latlng")
        except:
            address_longlat = None
        address = driver.find_element(By.XPATH, "//span[@data-node_tt_id='location_score_tooltip']").text
        num_star = driver.find_elements(By.XPATH, "//span[@data-testid='rating-squares']/span")
        rating = driver.find_element(By.XPATH, "//div[@data-testid='review-score-component']/div").text
        description = driver.find_element(By.ID, "property_description_content").text
        facilities = [item.text for item in driver.find_elements(By.CLASS_NAME, "important_facility")]
        item["name"] = hotel_name
        item["type"] = stay_type
        item["longlat"] = address_longlat
        item["address"] = address
        item["star"] = len(num_star)
        item["rating"] = rating
        item["description"] = description
        item["facilities"] = facilities
        # TODO: #hanLHN Crawler review and rating
        item["review"] = []
        # ============       Close tab       ===========
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        print(f">> Crawled {item['name']}")
        data.append(item)
    # ========================= Select next page =======================
    pages = driver.find_elements(By.XPATH, "//div[@data-testid='pagination']/nav/div/div[2]/ol/li")
    for i in range(len(pages)):
        num_class = len(pages[i].get_attribute("class").split())
        # Ignore previous page
        if num_class == 1:
            continue
        # Now is current select page
        # Break if the last page
        if i == len(pages) - 1:
            print(f">> Have no next page")
            has_next = False
            break
        # Else selection next page
        pages[i+1].click()
        print(f">> Select next page")
        break

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f)
driver.close()