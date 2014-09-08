# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class YpSpiderItem(Item):
    # define the fields for your item here like:
    title = Field()
    streetAddress = Field()
    city = Field()
    region = Field()
    zipcode = Field()
    phone = Field()
    
