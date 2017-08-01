# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from comments_scraper.items import CommentItem, ArticleItem
import urllib.parse as urlparse
import logging
import time
import datetime

class ZeitSpider(CrawlSpider):
    name = 'zeit'
    allowed_domains = ['www.zeit.de', 'community.zeit.de']
    start_urls = ['http://www.zeit.de/index']

    custom_settings = {"DOWNLOADER_MIDDLEWARES": {'comments_scraper.middlewares.JSMiddleware': 543,},}

    rules = [
        Rule(LinkExtractor(allow=['\/[a-z\/]*\/\d*\-\d*\/[a-z0-9-]*']),
        callback='parse_site',
        follow=True)
    ]

    def parse_site(self, response):
        #only scrape article for mainpage
        if response.url.find("?page") == -1:
            yield self.scrape_article(response)

        selector_list = response.css('div.comment__container')
        #todo cut out the ?\w* part from article + comment
        article_link = response.url
        for selector in selector_list:
            yield self.scrape_comment(article_link, selector)

        next_link = response.css('a.pager__button.pager__button--next').xpath("@href").extract_first()
        if next_link:
            yield Request(next_link, self.parse_site, method="GET", priority=100)

    def scrape_comment(self, article_link, comment_selector):
        comment = CommentItem()
        comment['id'] = comment_selector.xpath(".//a[@class='comment__reaction js-reply-to-comment']/@data-cid").extract_first()
        comment['user_name'] = comment_selector.xpath("div[@class='comment-meta']/div[@class='comment-meta__name']/a/text()").extract_first()
        comment['user_link'] = comment_selector.xpath("div[@class='comment-meta']/div[@class='comment-meta__name']/a/@href").extract_first()
        comment['content'] = comment_selector.xpath("div[@class='comment__body']/p/text()").extract()
        comment['removed'] = comment_selector.xpath(".//em[@class=moderation]/text()").extract_first()
        comment['upvotes'] = comment_selector.xpath(".//span[@class='js-comment-recommendations']/text()").extract_first()
        comment['quote'] = self.get_reply_to(comment_selector.xpath(".//a[@class='comment__origin js-jump-to-comment']/@href").extract_first())
        comment['comment_link'] = comment_selector.xpath(".//a[@class='comment-meta__date']/@href").extract_first()
        comment['article_id'] = self.extract_id_from_url(article_link)
        comment['article_link'] = article_link

        return comment

    def scrape_article(self, response):
        time_scraped = time.time()

        article = ArticleItem()
        article['date'] = response.xpath("//div[@class='metadata']/time/text()").extract_first()
        article['scraped_time_stamp'] = datetime.datetime.fromtimestamp(time_scraped).strftime('%d.%m.%Y %H:%M')
        article['author'] = response.xpath("//a[@rel='author']/span[@itemprop='name']/text()").extract_first()
        article['category'] = self.extract_category_from_url(response.url)
        if response.url.find("?") == -1:
            article['url'] = response.url.split('?')[0]
        else:
            article['url'] = response.url
        article['id'] = self.extract_id_from_url(article['url'])

        return article

    def extract_category_from_url(self, url):
        return url.split('/')[3]

    def extract_id_from_url(self, url):
        url_as_array = url.split('/')
        if len(url_as_array) == 5:
            id = url_as_array[5]
        if len(url_as_array) == 6:
            id = url_as_array[5]

        if id.find('?'):
            return id.split('?')[0]

        return id

    def get_reply_to(self, url):
        if url:
            parsed = urlparse.urlparse(url)
            return urlparse.parse_qs(parsed.query)['cid']

    def get_comment_id(self, url):
        if url:
            parsed = urlparse.urlparse(url)
            return urlparse.parse_qs(parsed.query)['pid'][0]
