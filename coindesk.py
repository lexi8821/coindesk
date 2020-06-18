from lxml import html
import requests
import re
import time
import os
from handler import Handler
from formatter import TextFormatter
from dateutil import parser
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

URL = 'https://www.coindesk.com/news'
HEADER = {'Connection': 'keep-alive',
    'Expires': '-1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
}
PAGES = ['news', 'features', 'opinion', 'category/markets', 'category/tech',
    'category/business', 'category/policy-regulation', 'category/people']
BASE_URL = 'https://www.coindesk.com/'

class ContentError(Exception):
    pass

class Coindesk:
    def __init__(self):
        self.__version__ = "0.3"
        self.header = HEADER
        self.handler = Handler()
        options = Options()
        options.headless = True
        self.browser = webdriver.Firefox(options = options,
            service_log_path=os.path.devnull)
        self.assets_keys = ['title', 'author', 'published', 'updated', 'tags',
            'link', 'text']

    def __del__(self):
        self.browser.quit()

    def _download(self, link, clicks=None):
        """
        Gets webpage source code by acting like a real person - clicking and
        scrolling for "another set of articles" element.
        """
        # Open headless browser with specified link
        self.browser.get(link)
        if clicks:
            # Sets up actions fro browser
            action = webdriver.ActionChains(self.browser)
            while clicks != 0:
                # Waits 5 seconds while all elements are loaded
                time.sleep(5)
                # Gets hight of the loaded window
                last_height = self.browser.execute_script("return document.body.scrollHeight")
                try:
                    # Finds "more articles" element
                    #element = self.browser.find_element_by_xpath('//div[@class="cta-content"]')
                    element = self.browser.find_element_by_xpath('//div[@class="cta-story-stack"]')
                except:
                    return None
                # Finds position of the element - top left corner in the window
                pos = element.location['y'] - element.size['height']
                # Scrolls window to that position
                self.browser.execute_script(f"window.scrollTo(0, {pos});")
                #action = webdriver.ActionChains(self.browser)
                # Moves cursor over the element
                action.move_to_element(element).perform()
                # Waits 1 second just like a real user
                time.sleep(1)
                try:
                    # Clicks element to load next batch of articles
                    element.click()
                    #self.browser.find_element_by_xpath('//div[@class="cta-content"]').click()
                    # Counds down clicks number
                    clicks -= 1
                except:
                    return None
        return self.browser.page_source

    def front_articles(self, link, clicks=None):
        content = self._download(link, clicks=clicks)
        if not content:
            return None
        tree = html.fromstring(content)
        headings = tree.xpath('//section[@class="list-body"]//h4[@class="heading"]/text()')
        authors = tree.xpath('//span[@class="credit"]/a/text()')
        times = tree.xpath('//section[@class="list-body"]//time[@class="time"]/text()')
        links = tree.xpath('//section[@class="list-body"]//div[@class="text-content"]/a[2]/@href')
        links = ['https://www.coindesk.com' + i for i in links]
        tags = tree.xpath('//section[@class="list-body"]//div[@class="text-content"]/a[1]/span/text()')
        return list(zip(headings, authors, times, links, tags))

    def article(self, link):
        content = self._download(link)
        tree = html.fromstring(content)
        # They change this element often!!!
        times = tree.xpath('//div[@class="timestamps"]/time/text()')
        if not times:
            times = tree.xpath('//div[@class="datetime"]/time/text()')
        if not times:
            times = tree.xpath('//div[@class="article-hero-datetime"]/time/text()')
        # Need to redo this string position in list is fixed - it will break-up fast!!!
        try:
            published = times[0]
            published = parser.parse(published)
            if len(times) == 2:
                updated = times[1].strip('Updated ')
                updated = parser.parse(updated)
            elif len(times) == 3:
                updated = times[2]
                updated = parser.parse(updated)
            else:
                updated = times[0]
                updated = parser.parse(updated)
        except:
            print(f"Error: No date at: {link}")
            published = ""
            updated = ""
        tf = TextFormatter()
        text = tf.format(content, link)
        return [published, updated, text]

    def aggregator(self, link, limit=50):
        """ Makes sure that number of articles are downloaded that are in the
            limit. """
        clicks = 0
        articles = self.front_articles(link, clicks=clicks)
        assets, items = self.back_articles(articles)
        while items < limit:
            clicks += 1
            articles = self.front_articles(link, clicks=clicks)
            if not articles:
                return None, None
            assets, items = self.back_articles(articles)
        return assets, items

    def back_articles(self, articles):
        assets = {}
        counter = 0
        for item in articles:
            article = {}
            article[self.assets_keys[0]] = item[0]
            id = self.handler.check_article(article)
            if not id:
                article[self.assets_keys[1]] = item[1]
                article[self.assets_keys[5]] = item[3]
                article[self.assets_keys[4]] = item[4]
                article_components = self.article(item[3])
                article[self.assets_keys[2]] = article_components[0]
                article[self.assets_keys[3]] = article_components[1]
                article[self.assets_keys[6]] = article_components[2]
                id = self.handler.insert_article(article)
                print(f"{id}: {article[self.assets_keys[0]]}.")
            else:
                article = self.get_article(id)
            assets[id] = article
            counter += 1
        return assets, counter

    def get_article(self, id):
        items = self.handler.get_article(id)
        if items:
            article = {}
            article[self.assets_keys[0]] = items[0]
            article[self.assets_keys[1]] = items[1]
            article[self.assets_keys[2]] = items[2]
            article[self.assets_keys[3]] = items[3]
            article[self.assets_keys[4]] = items[4]
            article[self.assets_keys[5]] = items[5]
            article[self.assets_keys[6]] = items[6]
            return article

    def loop_text_handler(self, link):
        """ Function for handling article text parsing. """
        content = self._download(link)
        tf = TextFormatter()
        return tf.format(content, link)

    def main(self, limit=50, links=None):
        """ Main function for looping through subpages of coindesk. """
        if not links:
            links = [BASE_URL + i for i in PAGES]
        for link in links:
            print(f"Getting articles in {link}.")
            _, _ = self.aggregator(link, limit=limit)

    def reparse_article_texts(self, forced=False):
        """ This is a utility function for formatting old articles text into
        new text with paras. Do not need to to be run again. """

        ids = self.handler.get_ids()
        for id in ids:
            content = self.handler.get_content_by_id(id)
            if not '\n' in content or forced:
                link = self.handler.get_link_by_id(id)
                text = self.loop_text_handler(link)
                self.handler.update_content_by_id(id, text)
                print(f"Article ID: {id} updated.")
                time.sleep(5)
            else:
                continue

if __name__ == '__main__':
    import sys
    coindesk = Coindesk()
    if len(sys.argv) >= 2:
        coindesk.main(limit=int(sys.argv[1]))
    else:
        coindesk.main()
