from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd

options = webdriver.ChromeOptions()
# options.add_argument("headless")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)
driver.get(r"https://www.booking.com/index.vi.html?")
wait = WebDriverWait(driver, 20)

# Data store
comments = []
comment_type = []
rating = []
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
        try:
            # Item data
            item = {}
            # Open item in new tab
            link.click()
            driver.switch_to.window(driver.window_handles[-1])
            # =========== Crawling in new tab =============
        except:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            print(">> Close due to error")
            continue


        # TODO: #hanLHN Crawler review and rating
        try:
            btn_review = driver.find_element(By.XPATH, "//*[@id='guest-featured_reviews__horizontal-block']/div/div[10]/button")
            btn_review.click()
            sleep(2)
            check_btn_review = True
        except Exception as e:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            print(">> Close due to error")
            continue

        if check_btn_review:
            # Change to vietnames review
            driver.execute_script('document.querySelector("#review_lang_filter").querySelectorAll(".bui-dropdown-menu__button")[1].click()')
            sleep(2)
            #----------------------------

            review_has_next = True
            review_page_number = 0

            while review_has_next:
                review_page_number += 1
                print("Review page: ", review_page_number)
                try:
                    elem = driver.find_element(By.XPATH, "//*[@id='review_list_page_container']/ul")
                    all_li = elem.find_elements(By.CLASS_NAME, "review_list_new_item_block")                
                    for i, li in enumerate(all_li):
                        try:
                            score = li.find_element(By.CLASS_NAME, "bui-review-score__badge").text
                            comment_block = li.find_elements(By.XPATH, "//*[@id='review_list_page_container']/ul/li["+str(i+1)+"]/div/div[2]/div[2]/div[2]/div/div[1]/p")
                            icon = comment_block[0].find_elements(By.TAG_NAME, "span")[0]
                            comment = comment_block[0].find_element(By.CLASS_NAME, "c-review__body").text
                            if comment == "Không có bình luận nào cho đánh giá này":
                                review_has_next = False
                                break
                            elif "c-review__prefix--color-green" in icon.get_attribute("class"):
                                comments.append(comment)
                                comment_type.append("positive")
                                rating.append(score)
                                print(comment, "pos", score)

                            else:
                                comments.append(comment)
                                comment_type.append("negative")
                                rating.append(score)
                                print(comment, "neg", score)
                                

                        except Exception as e:
                            print(f"Error get cmt: {e}")

                        
                except:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    print(">> Close due to error")
            
                if not review_has_next:
                    break
                try:
                    review_pages = driver.find_elements(By.CLASS_NAME, "bui-pagination__item")
                    if len(review_pages) == 0:
                        print(">> Reach last review page")
                        review_has_next = False
                        break
                    for i in range(1, len(review_pages)-1):
                        class_ = review_pages[i].get_attribute("class").split()
                        if "bui-pagination__item--active" in class_:
                            if i >= len(review_pages) - 3:
                                print(">> Reach last review page")
                                review_has_next = False
                                break
                            # Else selection next page
                            
                            review_pages[i+1].find_element(By.CLASS_NAME, "bui-pagination__link").click()
                            sleep(2)
                            break
                except Exception as e:
                    print(f"Error {e}")
                    review_has_next = False
        # ============       Close tab       ===========
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    # =========================== Save ==========================
    df = pd.DataFrame({
        "comments": comments,
        "type": comment_type,
        "rating": rating
    })
    print(df)
    df.to_csv("reviews.csv")
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
        sleep(3)
        break
    


driver.close()