import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

PAGES = ['news', 'features', 'opinion', 'category/markets', 'category/tech',
    'category/business', 'category/policy-regulation', 'category/people']
BASE_URL = 'https://www.coindesk.com/'

options = Options()
browser = webdriver.Firefox(options = options,
    service_log_path=os.path.devnull)

link = BASE_URL + PAGES[0]
browser.get(link)
clicks = 5
if clicks:
    action = webdriver.ActionChains(browser)
    while clicks != 0:
        time.sleep(10)
        last_height = browser.execute_script("return document.body.scrollHeight")
        try:
            element = browser.find_element_by_xpath('//div[@class="cta-content"]')
        except:
            continue
        pos = element.location['y'] - element.size['height']
        browser.execute_script(f"window.scrollTo(0, {pos});")

        action.move_to_element(element).perform()
        time.sleep(1)
        element.click()
        clicks -= 1
    source = browser.page_source
