# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from selenium import webdriver
from comments_scraper.items import CommentItem
from scrapy.exceptions import IgnoreRequest
from random import randint
import logging
import time
import datetime

class FazSpider(scrapy.Spider):
    name = 'faz'
    allowed_domains = ['faz.net']
    start_urls = ['http://www.faz.net/suche/?offset=&cid=&index=&query=&offset=&allboosted=&boostedresultsize=%24boostedresultsize&from=01.07.2017&to=06.08.2017&chkBox_2=on&BTyp=lesermeinungen&author=&username=&sort=date&resultsPerPage=80']

    base_url = "http://www.faz.net{}"
    suffix = "&BTyp=lesermeinungen&author=&username=&sort=date&resultsPerPage=80"
    def parse(self, response):
        selector_list = response.css('div.LeserkommentarInner')
        logging.info("parsing comments... on url {}".format(response.url))
        logging.info("has found {} comments".format(len(selector_list)))
        for selector in selector_list:
            yield self.create_comment(selector)

        infix = response.xpath('.//a[@title="Nächste Seite"]/@href').extract_first()
        if infix:
            next_link = self.base_url.format(infix)
            link_wo_hash = next_link.split('#')[0]
            yield Request(link_wo_hash + self.suffix, self.parse, method="GET")

    def create_comment(self, comment_selector, id = None, article = None):
        nameArray = comment_selector.xpath('div[@class="Status"]//a/span[@class="Username"]/text()').extract_first()
        time_scraped = time.time()

        comment = CommentItem()
        comment['scraped_time_stamp'] = datetime.datetime.fromtimestamp(time_scraped).strftime('%d.%m.%Y %H:%M')
        comment['user_name'] = comment_selector.xpath('div[@class="Status"]/a/span[@class="userId"]/text()').extract_first()
        if nameArray:
            nameArray = nameArray.split()
            comment['fore_name'] = nameArray[0]
            comment['last_name'] = nameArray[1]
        comment['upvotes'] = comment_selector.xpath('div[@class="Status"]/span[@class="StatusEmpfehlungen"]/text()').extract_first()
        comment['date'] = self.format_date(comment_selector.xpath('div[@class="Status"]/span[@class="Datetime"]/text()').extract_first())
        comment['user_link'] = comment_selector.xpath('div[@class="Status"]/a[@class="Username"]/@href').extract_first()
        comment['article_link'] = comment_selector.xpath('.//a[@class="LKArticleLink"]/@href').extract_first()
        comment['article_id'] = comment_selector.xpath('.//span[@class="Headline"]/text()').extract_first()
        comment['title'] = comment_selector.xpath('.//a[@class="LMArrowDown"]/text()').extract_first()
        comment['content'] = self.glue_string_array(comment_selector.xpath('p[@class="LeserkommentarText"]/text()').extract())
        comment['quote'] = self.get_answers(comment_selector.xpath('.//div[@class="LeserkommentarAntwortInner"]'), comment['article_id'], comment['article_link'])

        #this i needed for answers...
        if id:
            comment['article_id'] = id
            comment['article_link'] = article

        return comment

    def get_answers(self, answer_selectors, id, link):
        answerArray = []
        if answer_selectors:
            for answer_selector in answer_selectors:
                answerArray.append(self.create_comment(answer_selector, id, link))
        return answerArray

    def format_date(self, date_string):
        return date_string[2:]

    def glue_string_array(self, array):
        glued = " ".join(array)
        return (" ".join(glued.split()))

    def set_faz_link(self, link):
        if link:
            return ('http://www.faz.net%s' % str(link))
