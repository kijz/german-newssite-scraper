# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from comments_scraper.items import CommentItem, ArticleItem
import time
import re
import datetime
import json
from ast import literal_eval

class WeltSpider(scrapy.Spider):
    name = 'welt'
    allowed_domains = ['welt.de']
    #TODO change limit
    start_urls = ['https://api-co.la.welt.de/api/documents?sort=MOST_COMMENTED&limit=2']

    comments_url = "https://api-co.la.welt.de/api/comments?document-id={}&sort=NEWEST"
    answers_url = "https://api-co.la.welt.de/api/comments?document-id={}&parent-id={}&created-cursor={}"
    more_comments_url = "https://api-co.la.welt.de/api/comments?document-id={}&sort=NEWEST&created-cursor={}"

    user_url = "https://api-co.la.welt.de/api/public-users/{}"
    user_comments_url = "https://api-co.la.welt.de/api/comments?user-id={}&sort=MOST_POPULAR"
    more_user_comments_url = "https://api-co.la.welt.de/api/comments?user-id={}&sort=MOST_POPULAR&created-cursor={}&likes-cursor={}"

    #www.welt.de/{documentId}
    #https://api-co.la.welt.de/api/public-users/5955202fcff47e0001275c14
    def parse(self, response):
        print ("parsing documents... on url {}".format(response.url))
        formatted_json = response.body.decode()
        my_json = json.loads(formatted_json)

        for document in my_json:
            yield document

            yield Request(self.comments_url.format(document['id']), self.parse_comments, method="GET", priority=1)

    def parse_comments(self, response):
        #data = json.loads(response.body)
        # Decode UTF-8 bytes to Unicode, and convert single quotes
        print ("parsing comments... on url {}".format(response.url))
        formatted_json = response.body.decode()
        my_json = json.loads(formatted_json)
        comments = my_json['comments']

        for comment in my_json['comments']:
            if comment['childCount'] > 1:
                url = self.answers_url.format(comment['documentId'], comment['id'], comment['created'])
                yield Request(url, self.parse_anwers, method="GET", priority=100)

            ''' get to user profile and scraping data '''
            yield Request(self.user_url.format(comment['user']['id']), self.parse_user, method="GET", priority=100)

        if len(comments) >= 10:
            offset = 1
            last_comment = comments[len(comments) - offset]
            while True:
                ''' point the array cursor on the last item without parent
                to make next request on api'''
                try:
                    offset += 1
                    if last_comment['parentId']:
                        last_comment = comments[len(comments) - offset]
                except:
                    break

            url = self.more_comments_url.format(last_comment['documentId'], last_comment['created'])
            yield Request(url, self.parse_comments, method="GET", priority=10)

    def parse_anwers(self, response):
        #data = json.loads(response.body)
        # Decode UTF-8 bytes to Unicode, and convert single quotes
        print ("parsing answers... on url {}".format(response.url))

        formatted_json = response.body.decode()
        my_json = json.loads(formatted_json)
        comments = my_json['comments']

        #skip first because its already scraped
        for comment in comments[1:]:
            yield Request(self.user_url.format(comment['user']['id']), self.parse_user, method="GET", priority=100)

    def parse_user(self, response):
        print ("parsing user... on url {}, scraping data now".format(response.url))
        formatted_json = response.body.decode()
        user = json.loads(formatted_json)

        yield user
        if not user['privateProfile']:
            yield Request(self.user_comments_url.format(user['id']), self.parse_user_comments, method="GET", priority=500)

    def parse_user_comments(self, response):
        print ("parsing user_comments... on url {}".format(response.url))
        formatted_json = response.body.decode()
        my_json = json.loads(formatted_json)
        comments = my_json['comments']

        for comment in comments:
            yield comment

        if len(comments) >= 5:
            last = comments[-1]
            url = self.more_user_comments_url.format(last['user']['id'], last['created'], last['likes'])
            yield Request(url, self.parse_user_comments, method="GET", priority=1000)

    def extract_category_from_url(self, url):
        return url.split('/')[3]
