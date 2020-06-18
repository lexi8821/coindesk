import re
from lxml import html

class ContentError(Exception):
    pass

class TextFormatter:
    """ This class formats the coindesk html article content into homogenous
        text. """
    def __init__(self):
        pass

    def format(self, content, link):
        """ Function for parsing and formatting article text. """
        error = None
        # Phase 1 - setting correct xpath -> what to include as text from html
        tree = html.fromstring(content)
        # TODO: They change this often!!!
        texts = tree.xpath('//section[starts-with(@class,"article-body")]/div[starts-with(@id, "node-") and not(descendant::figcaption)]//text()')
        if not texts:
            texts = tree.xpath('//section[contains(@class,"article-body")]/div[starts-with(@id, "node-") and not(descendant::figcaption)]//text()')
        if not texts:
            texts = tree.xpath('//div[@class="classic-body"]/p//text()')
        # There are also articles that show 404
        # This should be error message in Coindesk.article() as 404 articles
        # does not have dates
        if not texts:
            try:
                error = tree.xpath('//section[@class="error-module"]')[0]
            except:
                error = None
        # There are article that have no text
        if not texts:
            try:
                empty_article = tree.xpath('//section[contains(@class,"article-body")]')[0]
            except IndexError:
                empty_article = None
        # If article has no text, does not show 404 error it is time to update xpath
        # This need to be tested on more articles !!!
        if not texts and empty_article is None and error is None:
            raise ContentError(f"ERROR: Update xpath for text {link} !!!")
        elif not texts and empty_article is None and error is not None:
            return "404"
        else:
            return 'No text available'
        para = []
        j = []
        # Phase 2 - connecting appropriate items in paras list
        text_list = [re.sub(r'[\xa0]', '', i) for i in texts]
        for i in text_list:
            if i.endswith('.') or i.endswith('."') or i.endswith('. ') or i.endswith('.”') or i.endswith('.’”'):
                if j:
                    j.append(i)
                    para.append(j)
                    j = []
                else:
                    para.append(i)
            else:
                try:
                    next_space = text_list[text_list.index(i) + 1].startswith(' ')
                    next_capital = text_list[text_list.index(i) + 1][0].isupper()
                except IndexError:
                    next_space = False
                    next_capital = False
                if next_space and next_capital:
                    para.append(i)
                else:
                    j.append(i)
        # Phase 3 - final formatting corrections from list of paras to fluent text
        paras = [' '.join(i) if isinstance(i, list) else i for i in para]
        paras = [re.sub(r' +', ' ', i).strip() for i in paras]
        paras = [str(i) + '\n' for i in paras]
        return ' '.join(paras)
