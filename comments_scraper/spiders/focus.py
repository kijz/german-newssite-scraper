# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from comments_scraper.items import CommentItem
import time
import re
import datetime

class FocusSpider(scrapy.Spider):
    name = 'focus'
    allowed_domains = ['focus.de']
    #start_urls = ['http://www.focus.de/community/ranglisten/most-comments/']
    #custom_settings = {"DOWNLOADER_MIDDLEWARES": {'comments_scraper.middlewares.JSMiddleware': 543,},}
    start_urls = ['http://www.focus.de/auto/elektroauto/adac-testet-nissan-leaf-batterie-alterung-elektroauto-reichweite-sinkt-nach-fuenf-jahren-auf-90-kilometer_id_7400203.html']

    #rules = [
    #    Rule(LinkExtractor(allow=['\/\w*\/\w*\/[\w*-]*.html']),
    #    callback='parse_site',
    #    follow=True)
    #]

    def parse(self, response):
        '''
        Find the first comment (if present), and follow the comment pagination
        '''

        selector = response.css('div.comment')[0]
        yield self.get_comment(selector, response.url)

    def parse_comment(self, response):
        '''
        Follow pageination and crawl each comment
        '''
        selector = response.css('div#article')

        yield self.create_comment(response.url, selector)

        next_url_suffix = selector.xpath('.//a[@class="nextPage"]/@href').extract_first()
        if next_url_suffix:
            print("response.url : " + response.url)
            print("next_url_suffix : " + next_url_suffix)
            yield Request(self.create_comment_url(next_url_suffix, response.url), self.parse_comment, method="GET")

    def create_comment(self, comment_link, comment_selector):
        time_scraped = time.time()
        print("comment_link: " + comment_link)
        comment = CommentItem()
        comment['id'] = self.extract_article_id(comment_link)
        comment['comment_link'] = comment_link
        comment['title'] = comment_selector.xpath('.//div[@class="articleHead"]/h1/text()').extract_first()
        comment['scraped_time_stamp'] = datetime.datetime.fromtimestamp(time_scraped).strftime('%d.%m.%Y %H:%M')
        comment['date'] = comment_selector.xpath('.//span[@class="created"]/text()').extract_first()
        comment['user_name'] = comment_selector.xpath('.//span[@class="created"]/a/text()').extract_first()
        comment['user_link'] = comment_selector.xpath('.//span[@class="created"]/a/@href').extract_first()
        comment['upvotes'] = comment_selector.xpath('.//div[@class="vote_area_v2"]').extract()
        comment['downvotes'] = comment_selector.xpath('.//div[@class="vote_area_v2"]').extract()
        comment['content'] = comment_selector.xpath('.//p[@class="textBlock"]/text()').extract_first()
        comment['quote'] = self.get_answers(comment_selector.xpath('.//div[@id="comments"]'))

        return comment

    def create_answer(self, comment_selector):
        time_scraped = time.time()

        comment = CommentItem()
        comment['title'] = comment_selector.xpath('.//span[@class="answerHead"]/text()').extract_first()
        comment['scraped_time_stamp'] = datetime.datetime.fromtimestamp(time_scraped).strftime('%d.%m.%Y %H:%M')
        comment['date'] = comment_selector.xpath('.//span[@class="created"]/text()').extract_first()
        comment['user_name'] = comment_selector.xpath('.//p[@class="user"]/a/text()').extract_first()
        comment['user_link'] = comment_selector.xpath('.//p[@class="user"]/a/@href').extract_first()
        comment['upvotes'] = comment_selector.xpath('.//div[@class="vote_area_v2"]').extract()
        comment['downvotes'] = comment_selector.xpath('.//div[@class="vote_area_v2"]').extract()
        comment['content'] = comment_selector.xpath('.//p[@class="text"]/text()').extract_first()

        return comment

    def get_answers(self, answer_selectors):
        answerArray = []
        if answer_selectors:
            for answer_selector in answer_selectors:
                answer = self.create_answer(answer_selector)
                if answer['content'] is not None:
                    answerArray.append(answer)
        return answerArray

    def get_comment(self, selector, article_link):
        suffix = selector.xpath(".//a[@class='toggleComment']/@href").extract_first()
        url = self.create_comment_url(suffix, article_link)
        return Request(url, self.parse_comment, method="GET")

    def create_comment_url(self, suffix, article_link):
        article_array = article_link.split('/')
        article_array[-1] = suffix
        return "/".join(article_array)

    def extract_article_id(self, url):
        article = re.search('kommentar_id_(\d+)', url).group(1)
        return re.search('(\d+)', article).group(1)
