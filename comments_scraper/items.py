# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

def remove_whitespaces(content):
    if isinstance(content, list):
        return " ".join(content)

    return (" ".join(content.split()))

class CommentItem(Item):
    # define the fields for your item here like:
    user_name = Field()
    fore_name = Field()
    last_name = Field()
    time_stamp = Field()
    upvotes = Field()
    downvotes = Field()
    recommendations = Field()
    date = Field()
    user_link = Field()
    comment_link = Field()
    article_link = Field()
    title = Field(serializer=remove_whitespaces)
    content = Field(serializer=remove_whitespaces)
    quote = Field()

class ArticleItem(Item):
    url = Field()
    category = Field()
    id = Field()
