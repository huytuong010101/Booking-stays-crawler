from selenium import webdriver
import webbrowser 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import json

options = webdriver.ChromeOptions()
# options.add_argument("headless")
driver = webdriver.Chrome(options=options)
driver.get(r"https://www.booking.com/index.vi.html?")
wait = WebDriverWait(driver, 20)

# Data store
data = []
# Search
elem = driver.find_element(By.NAME, "ss")
elem.clear()
elem.send_keys("Da Nang, Viet Nam")
elem.send_keys(Keys.RETURN)
sleep(2)
has_next = True
page_number = 0
# Now loop all page
while has_next:
    page_number += 1
    print('>> Now we on page' + str(page_number))
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
        sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
        sleep(1)
        try:
            btn_review = driver.find_element(By.XPATH, "//*[@id='guest-featured_reviews__horizontal-block']/div/div[10]/button")
            btn_review.click()
            check_btn_review = True
        except Exception as e:
            check_btn_review = False
            print(f"Error: {e} \n There's no review")

        if check_btn_review:
            reviews = []

            review_has_next = True
            review_page_number = 0

            while review_has_next:
                review_page_number += 1
                print("Review page: ", review_page_number)
                sleep(3)
                elem = driver.find_element(By.XPATH, "//*[@id='review_list_page_container']/ul")
                all_li = elem.find_elements(By.CLASS_NAME, "review_list_new_item_block")                
                for i, li in enumerate(all_li):
                    review_item = {}
                    review_item['comment'] = []
                    review_item['score'] = ""

                    try:
                        review_item['review_title'] = li.find_element(By.XPATH, "//*[@id='review_list_page_container']/ul/li["+str(i+1)+"]/div/div[2]/div[2]/div[1]/div/div[1]/h3").text
                    except:
                        review_item['review_title'] = ""
                    pos_comment = ""
                    neg_comment = ""
                    try:
                        comment_block = li.find_elements(By.XPATH, "//*[@id='review_list_page_container']/ul/li["+str(i+1)+"]/div/div[2]/div[2]/div[2]/div/div[1]/p")
                        pos_icon = len(comment_block[0].get_attribute("class").split())
                        if pos_icon > 1:
                            pos_comment = comment_block[0].find_element(By.CLASS_NAME, "c-review__body").text
                            review_item['comment'].append({"pos_cmt": pos_comment})

                        else:
                            neg_comment = comment_block[0].find_element(By.CLASS_NAME, "c-review__body").text
                            review_item['comment'].append({"neg_cmt": neg_comment})

                    except Exception as e:
                        print(f"Error get cmt: {e}")

                    score = li.find_element(By.CLASS_NAME, "bui-review-score__badge").text
                    review_item['score'] = score
                    reviews.append(review_item)
            
                try:
                    review_pages = driver.find_element(By.XPATH, "//*[@id='review_list_page_container']/div[4]/div/div[1]/div/div[2]/div")
                    for i in range(len(review_pages)):
                        review_num_class = len(review_pages[i].get_attribute("class").split())
                        
                        if review_num_class == 1:
                            continue

                        if i == len(review_pages) - 1:
                            review_has_next = False
                            break
                        # Else selection next page
                        review_pages[i+1].click()
                        break
                except Exception as e:
                    print(f"Error {e}")
                    review_has_next = False
            print(reviews)
            item["review"] = reviews
        # ============       Close tab       ===========


        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        print(">> Crawled" + str(item['name']))
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
            print(">> Have no next page")
            has_next = False
            break
        # Else selection next page
        pages[i+1].click()
        print(">> Select next page")
        break

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f)
driver.close()