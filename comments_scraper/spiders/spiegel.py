# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from comments_scraper.items import CommentItem, ArticleItem
import time
import re
import datetime

class SpiegelSpider(CrawlSpider):
    name = 'spiegel'
    allowed_domains = ['spiegel.de']
    start_urls = [
    'http://www.spiegel.de/forum/politik/index-3.html',
    'http://www.spiegel.de/forum/politik/index-4.html',
    'http://www.spiegel.de/forum/politik/index-5.html',
    'http://www.spiegel.de/forum/politik/index-6.html',
    'http://www.spiegel.de/forum/politik/index-7.html',
    'http://www.spiegel.de/forum/politik/index-8.html',
    'http://www.spiegel.de/forum/politik/index-9.html',
    'http://www.spiegel.de/forum/politik/index-10.html',
    'http://www.spiegel.de/forum/politik/index-11.html',
    'http://www.spiegel.de/forum/politik/index-12.html',
    'http://www.spiegel.de/forum/politik/index-13.html',
    'http://www.spiegel.de/forum/politik/index-14.html',
    'http://www.spiegel.de/forum/politik/index-15.html',
    'http://www.spiegel.de/forum/politik/index-16.html',
    'http://www.spiegel.de/forum/politik/index-17.html',
    'http://www.spiegel.de/forum/politik/index-18.html',
    'http://www.spiegel.de/forum/politik/index-19.html',
    'http://www.spiegel.de/forum/politik/index-20.html',
    'http://www.spiegel.de/forum/politik/index-21.html',
    'http://www.spiegel.de/forum/politik/index-22.html',
    'http://www.spiegel.de/forum/politik/index-23.html',
    'http://www.spiegel.de/forum/politik/index-24.html',
    'http://www.spiegel.de/forum/politik/index-25.html',
    'http://www.spiegel.de/forum/politik/index-26.html',
    'http://www.spiegel.de/forum/politik/index-27.html',
    'http://www.spiegel.de/forum/politik/index-28.html'
    ]
    count_articles = 0

    def parse(self, response):
        selector_list = response.css('div.threadbit')
        for selector in selector_list:
            article_link = self.set_spiegel_link(selector.xpath('.//div[@class="thread-content"]/a/@href').extract_first())

            self.count_articles += 1
            print("Article count: {}".format(self.count_articles))
            print("Article link: {}".format(article_link))

            yield Request(article_link, self.parse_article, method="GET", priority=10)

        next_site = self.set_spiegel_link(response.css('a.page-next').xpath("@href").extract_first())
        #if next_site:
        #    yield Request(next_link, self.parse, method="GET", priority=1)

    def parse_article(self, response):
        selector_list = response.css('div.postbit')
        article_link = response.css('div.sysopPost').xpath('div/a[@class="button"]/@href').extract_first()

        for selector in selector_list:
            yield self.create_comment(response.url, article_link, selector)

        next_page = self.set_spiegel_link(response.css('a.page-next').xpath("@href").extract_first())
        if next_page:
            yield Request(next_page, self.parse_article, method="GET", priority=100)


    def create_comment(self, forum_link, article_link, selector):
        time_scraped = time.time()

        comment = CommentItem()
        comment['scraped_time_stamp'] = datetime.datetime.fromtimestamp(time_scraped).strftime('%d.%m.%Y %H:%M')
        comment['user_name'] = selector.xpath('div/a/b/text()').extract_first()
        comment['date'] = selector.xpath('.//span[@class="date-time"]/text()').extract_first()
        comment['user_link'] = self.set_spiegel_link(selector.xpath('div/a/@href').extract_first())
        comment['comment_link'] = self.set_spiegel_link(selector.xpath('div/a[@class="postcounter"]/@href').extract_first())
        comment['article_link'] = article_link
        comment['title'] = selector.xpath('div/a[@class="postcounter"]/text()').extract_first()
        comment['content'] = selector.xpath('div/p/span[@class="postContent"]/text()').extract_first()
        comment['quote'] = selector.xpath('div/p/span/span[@class="quote"]/a/@href').extract_first()
        if comment['quote']:
            comment['quote'] = self.set_spiegel_link(comment['quote'])
        comment['article_id'] = self.extract_id_from_url(forum_link)

        return comment

    def set_spiegel_link(self, link):
        if link:
            return ('http://www.spiegel.de%s' % str(link))
        #extract comment section and get next site of comments

    def extract_id_from_url(self, url):
        article = re.search('(thread-\d*)', url).group(1)
        return article.split('-')[1]
