# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from comments_scraper.items import CommentItem


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
        selector_list = response.css('div.postbit')
        article_link = response.css('div.sysopPost').xpath('div/a[@class="button"]/@href').extract_first()

        for selector in selector_list:
            comment = CommentItem()

            comment['user_name'] = selector.xpath('div/a/b/text()').extract_first()
            comment['fore_name'] = None
            comment['last_name'] = None
            comment['date'] = selector.xpath('//span[@class="date-time"]/text()').extract_first()
            comment['user_link'] = self.set_spiegel_link(selector.xpath('div/a/@href').extract_first())
            comment['comment_link'] = self.set_spiegel_link(selector.xpath('div/a[@class="postcounter"]/@href').extract_first())
            comment['article_link'] = article_link
            comment['title'] = selector.xpath('div/a[@class="postcounter"]/text()').extract_first()
            comment['content'] = selector.xpath('div/p/span[@class="postContent"]/text()').extract_first()
            comment['quote'] = selector.xpath('div/p/span/span[@class="quote"]/a/@href').extract_first()


            yield comment

    def set_spiegel_link(self, link):
        if link:
            return ('http://www.spiegel.de%s' % str(link))
        #extract comment section and get next site of comments
