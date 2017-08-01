# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from comments_scraper.items import CommentItem, ArticleItem
import time
import re
import datetime

class SpiegelSpider(CrawlSpider):
    name = 'spiegel'
    allowed_domains = ['spiegel.de']
    start_urls = ['http://spiegel.de/forum/']

    rules = [
        Rule(LinkExtractor(allow=['/forum/\w*/.*.html']),
        callback='parse_site',
        follow=True),
        Rule(LinkExtractor(allow=['/forum/member-\d*.html']),
        follow=True)
    ]

    def parse_site(self, response):
        if self.extract_page_number(response.url) == '1':
            yield self.get_article(response)

        selector_list = response.css('div.postbit')
        article_link = response.css('div.sysopPost').xpath('div/a[@class="button"]/@href').extract_first()

        for selector in selector_list:
            comment = CommentItem()

            comment['user_name'] = selector.xpath('div/a/b/text()').extract_first()
            comment['date'] = selector.xpath('.//span[@class="date-time"]/text()').extract_first()
            comment['user_link'] = self.set_spiegel_link(selector.xpath('div/a/@href').extract_first())
            comment['comment_link'] = self.set_spiegel_link(selector.xpath('div/a[@class="postcounter"]/@href').extract_first())
            comment['article_link'] = article_link
            comment['title'] = selector.xpath('div/a[@class="postcounter"]/text()').extract_first()
            comment['content'] = selector.xpath('div/p/span[@class="postContent"]/text()').extract_first()
            comment['quote'] = selector.xpath('div/p/span/span[@class="quote"]/a/@href').extract_first()
            comment['article_id'] = self.extract_id_from_url(response.url)

            yield comment


    def get_article(self, response):
        time_scraped = time.time()

        article = ArticleItem()
        article['scraped_time_stamp'] = datetime.datetime.fromtimestamp(time_scraped).strftime('%d.%m.%Y %H:%M')
        article['category'] = response.xpath("//div[@class='article-title']/text()").extract_first()
        article['url'] = response.css('div.sysopPost').xpath('div/a[@class="button"]/@href').extract_first()
        article['id'] = self.extract_id_from_url(response.url)

        return article

    def set_spiegel_link(self, link):
        if link:
            return ('http://www.spiegel.de%s' % str(link))
        #extract comment section and get next site of comments

    def extract_id_from_url(self, url):
        article = re.search('(thread-\d*)', url).group(1)
        return article.split('-')[1]

    def extract_page_number(self, url):
        article = re.search('(\d\.html)', url).group(1)
        return re.search('(\d)', article).group(1)
