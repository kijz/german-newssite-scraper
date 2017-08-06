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

class FazSpider(Scrapy.spider):
    name = 'faz'
    allowed_domains = ['faz.net']
    start_urls = ['http://www.faz.net/suche/?offset=&cid=&index=&query=&offset=&allboosted=&boostedresultsize=%24boostedresultsize&from=01.07.2017&to=06.08.2017&chkBox_2=on&BTyp=lesermeinungen&author=&username=&sort=date&resultsPerPage=80']

    base_url = "http://www.faz.net{}"
    def parse(self, response):
        selector_list = response.css('div.LeserkommentarInner')
        logging.info("has found {} comments".format(len(selector_list)))
        for selector in selector_list:

            #TODO yield self.get_article()
            comment = self.create_comment(selector)
            yield comment

        suffix = response.xpath('.//a[@rel="next"]/@href').extract(first)
        if suffix:
            next_link = base_url.format(suffix)
            yield Request(next_link, self.parse, method="GET")

    def create_comment(self, comment_selector):
        nameArray = comment_selector.xpath('span[@class="Username"]/a/span/span[@class="truncate truncate300"]/text()').extract_first()

        comment = CommentItem()
        comment['user_name'] = comment_selector.xpath('span[@class="Username"]/a/@data-loginname').extract_first()
        if nameArray:
            nameArray = nameArray.split()
            comment['fore_name'] = nameArray[0]
            comment['last_name'] = nameArray[1]
        comment['upvotes'] = comment_selector.xpath('.//span[@class="StatusEmpfehlungen"]/text()').extract_first()
        comment['recommendations'] = comment_selector.xpath('span[@class="Username"]/a/span/span[@class="greenTxt truncate bold"]/text()').extract_first()
        comment['date'] = self.format_date(comment_selector.xpath('.//span[@class="Datetime"]/text()').extract_first())
        comment['user_link'] = comment_selector.xpath('.//span[@class="Username"]/a/@href').extract_first()
        comment['article_link'] = article_link
        comment['title'] = comment_selector.xpath('.//a[@class="LMArrowDown"]/text()').extract_first()
        comment['content'] = self.glue_string_array(comment_selector.xpath('.//div[@class="LeserkommentarText"]/text()').extract())
        comment['quote'] = self.get_answers(comment_selector.xpath('.//div[@class="LeserkommentarAntwort"]/div[@class="LeserkommentarAntwortInner"]'))
        return comment

    def get_answers(self, answer_selectors):
        answerArray = []
        if answer_selectors:
            for answer_selector in answer_selectors:
                answerArray.append(self.create_comment(answer_selector))
        return answerArray

    def format_date(self, date_string):
        return date_string[3:]

    def glue_string_array(self, array):
        glued = " ".join(array)
        return (" ".join(glued.split()))

    def set_faz_link(self, link):
        if link:
            return ('http://www.faz.net%s' % str(link))
