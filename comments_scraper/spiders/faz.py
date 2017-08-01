# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from selenium import webdriver
from comments_scraper.items import CommentItem, ArticleItem
from scrapy.exceptions import IgnoreRequest
from random import randint
import logging
import time

class FazSpider(CrawlSpider):
    name = 'faz'
    allowed_domains = ['faz.net']
    start_urls = ['http://www.faz.net/aktuell/']
    custom_settings = {"DOWNLOADER_MIDDLEWARES": {'comments_scraper.middlewares.JSMiddleware': 543,},}

    rules = [
        Rule(LinkExtractor(allow=['/\w*/\w*/.*.html']),
        callback='parse_site',
        follow=True),
        Rule(LinkExtractor(allow=['/suche/.*']),
        follow=True)
    ]

    def parse_site(self, response):
        article_link = response.url
        selector_list = response.css('div#TabLesermeinungContent_AlleMeinungen>.LMFuss')
        logging.info("has found {} comments".format(len(selector_list)))
        for selector in selector_list:
            print (selector)
            comment = self.create_comment(article_link, selector)
            yield comment
        '''
        LOGGER.setLevel(logging.WARNING)
        logging.info('PhantomJS for Faz started!')
        #Create webdriver
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36")
        driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs-2.1.1-linux-x86_64/bin/phantomjs',desired_capabilities=dcap)
        driver.get(article_link)

        wait = WebDriverWait(driver, 30)
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')

        #wait for slow ass site to load...
        time.sleep(30)
        #First click button to show more than 5...
        try:
            logging.info("try button on '{}'".format(driver.current_url))
            next = driver.find_element_by_css_selector('.mehr')
            logging.info("found on '{}'".format(driver.current_url))
            next.click()
            logging.info("clicked on '{}'".format(driver.current_url))
            time.sleep(randint(5, 9))
            logging.info("Has slept")
        except Exception as e:
            logging.info('no more comments button fond')

        selector_list = response.css('div#TabLesermeinungContent_AlleMeinungen>.LMFuss')
        logging.info("has found {} comments".format(len(selector_list)))
        for selector in selector_list:
            print (selector)
            comment = self.create_comment(article_link, selector)
            yield comment

        #Then follow the pagination...
        while True:
            try:
                logging.info("try button on '{}'".format(driver.current_url))
                next = driver.find_element_by_css_selector('.icon-page_finanzen_next')
                logging.info("found on '{}'".format(driver.current_url))
                next.click()
                logging.info("clicked on '{}'".format(driver.current_url))
                time.sleep(randint(10, 15))
                logging.info("Has slept")

                selector_list = response.css('div#TabLesermeinungContent_AlleMeinungen>.LMFuss')
                logging.info("has found {} comments".format(len(selector_list)))
                for selector in selector_list:
                    print (selector)
                    comment = self.create_comment(article_link, selector)
                    yield comment

            except Exception as e:
                logging.info('no buttons found / end of traversing')
                break
        '''
    
    def create_comment(self, article_link, comment_selector):
        nameArray = comment_selector.xpath('span[@class="Username"]/a/span/span[@class="truncate truncate300"]/text()').extract_first()

        comment = CommentItem()
        comment['user_name'] = comment_selector.xpath('span[@class="Username"]/a/@data-loginname').extract_first()
        if nameArray:
            nameArray = nameArray.split()
            comment['fore_name'] = nameArray[0]
            comment['last_name'] = nameArray[1]
        comment['upvotes'] = comment_selector.xpath('span/span[@class="recommsAmount"]/text()').extract_first()
        comment['recommendations'] = comment_selector.xpath('span[@class="Username"]/a/span/span[@class="greenTxt truncate bold"]/text()').extract_first()
        comment['date'] = self.format_date(comment_selector.xpath('span[@class="Username"]/span[@class="grayTxt dateTime"]/text()').extract_first())
        comment['user_link'] = self.set_faz_link(comment_selector.xpath('span[@class="Username"]/a/@href').extract_first())
        comment['article_link'] = article_link
        comment['title'] = comment_selector.xpath('span[@class="LMFussLink"]/text()').extract_first()
        comment['content'] = self.glue_string_array(comment_selector.xpath('div[@class="LMText"]/text()').extract())
        comment['quote'] = self.get_answers(comment_selector.xpath('div[@class="LMText"]/div[@class="LMAntwortWrapper"]/div'))
        return comment

    def get_answers(self, answer_selectors):
        answerArray = []
        if answer_selectors:
            for answer_selector in answer_selectors:
                answerArray.append(self.create_comment(None, answer_selector))
        return answerArray

    def format_date(self, date_string):
        return date_string[3:]

    def glue_string_array(self, array):
        glued = " ".join(array)
        return (" ".join(glued.split()))

    def set_faz_link(self, link):
        if link:
            return ('http://www.faz.net%s' % str(link))
