# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import time
import json

class SzdethreadsSpider(scrapy.Spider):
    name = 'szdethreads'
    allowed_domains = ['disqus.com']
    start_urls = ['https://disqus.com/api/3.0/forums/listThreads.json?api_key=iNlxwT0sgkkM1yj2AaKnZGVJcSqJcJmdTAwogdoyKW94HQrGpchsWdFlIdtO9rk4&forum=szde']

    base_url_threads = "https://disqus.com/api/3.0/forums/listThreads.json?api_key=iNlxwT0sgkkM1yj2AaKnZGVJcSqJcJmdTAwogdoyKW94HQrGpchsWdFlIdtO9rk4&forum=szde&cursor={}"
    def parse(self, response):
        response_json = json.loads(response.body.decode())
        rate_limit_remaining = response.headers.get('X-Ratelimit-Remaining').decode()

        cursor = response_json['cursor']
        print ("Rate-Limit-Remaining: {}".format(rate_limit_remaining))
        print(cursor)

        for comment in response_json['response']:
            yield comment
        '''
        Free API key has 1000 requests per hour
        i chose to sleep ~(60 * 60 = 3600)  = (1000 * time.sleep(5) = 5000) to be safe
        '''
        if cursor['hasNext']:
            time.sleep(5)
            next_url = self.base_url_threads.format(cursor['next'])
            yield Request(next_url, self.parse, method="GET")
