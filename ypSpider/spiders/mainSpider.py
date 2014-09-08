import os
import csv
import time
from datetime import datetime
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
from ypSpider.items import YpSpiderItem

class YellowPagesSpider(BaseSpider):

    name = "yellowpages"	#Your Spider's name
    allowed_domains = ["yellowpages.com"]

    #Input your choices you want to search on yellowpages.com
    input_item = raw_input("Enter item's name you want to search for:")
    input_item = input_item.replace(' ', '-').strip(' ,.~!@#$%^&*()-+\\/\'')
    input_city_region = []
    input_city = raw_input("Enter your city you want to search in:")
    input_city_region.append(input_city)
    input_region = raw_input("Enter your region want to search in:")
    input_city_region.append(input_region)
    
    input_item_city_region = []								#It's file name and folder name to make searching for files easy
    
    input_item_city_region.append(input_item)
    input_item_city_region.append(input_city)
    input_item_city_region.append(input_region)
    
    join_string = "-"
    input_city_region = join_string.join(input_city_region)
    
    #To create a folder according your search query
    input_item_city_region = join_string.join(input_item_city_region)
    input_item_city_region = input_item_city_region.strip(' ,.~!@#$%^&*()-+\\/\'')
    
    start_urls = [
        "http://www.yellowpages.com/%s/%s"%(input_city_region, input_item),
    ]

    #csv_file = 'items.csv'								#File to store the data into .csv format
    csv_file = str(input_item_city_region)+'.csv'					#File to store the data into .csv format
    items = []			#Store your unstructured data into list
    
    fmt = '%Y-%m-%dT%H:%M:%SZ'
    local_datetime = datetime.fromtimestamp(time.time())
    
    count = 1

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        titles = hxs.select("//div[@class='v-card']")
	
	#Extract the requested unstructured data from all the pages of requested item on yellowpages.com
        for title in titles:
	    item = YpSpiderItem()
	    item['title'] = title.select(".//span[@itemprop='name']/text()").extract()
	    item['streetAddress'] = title.select(".//span[@itemprop='streetAddress']/text()").extract()
	    if len(item['streetAddress'])==0:
		item['streetAddress'] = title.select(".//p[@class='adr']/text()").extract()
	    item['city'] = title.select(".//span[@itemprop='addressLocality']/text()").extract()
	    item['region'] = title.select(".//span[@itemprop='addressRegion']/text()").extract()
	    item['zipcode'] = title.select(".//span[@itemprop='postalCode']/text()").extract()
	    item['phone'] = title.select(".//ul[@class='phones']/li[@itemprop='telephone']/text()").extract()
	    
	    if len(item['title'])!=0:
	    	(self.items).append(item)
		self.writeToCsv(item,self.csv_file)
	    else:
		pass

	#Check if next page is available to mine or not
    	next_page = hxs.select("//div[@class='pagination']/ul/li/a[@class='next ajax-page' and contains(text(), 'Next')]")

    	if next_page:
	    next_page_link = hxs.select("//div[@class='pagination']/ul/li/a[@class='next ajax-page']/@data-page").extract()
	    next_url = "http://www.yellowpages.com/%s/%s?g=%s&q=%s&page=%s&s=relevance"%(self.input_city_region, self.input_item, self.input_city_region, self.input_item, next_page_link[0])
            self.count = self.count + 1
            yield Request(next_url, self.parse)
            #print "%s"%str(self.count)
	    #return Request(next_url, self.parse)
	else:
	    print "All the pages has been scraped"
	
	self.convertToVCard(self.csv_file)
	
    #Write your extracted data to csv file
    def writeToCsv(self, row, csv_file_name):
		
	with open(csv_file_name, "a") as csv_file:
		if len(row['title'])!=0:
			csv_file.write((row['title'][0]).encode('utf-8').strip(' ,.'))
		csv_file.write(',')
		if len(row['streetAddress'])!=0:
			csv_file.write((row['streetAddress'][0]).encode('utf-8').strip(' ,.'))
		csv_file.write(',')
		if len(row['city'])!=0:
			csv_file.write((row['city'][0]).encode('utf-8').strip(' ,.'))
		csv_file.write(',')
		if len(row['region'])!=0:
			csv_file.write((row['region'][0]).encode('utf-8').strip(' ,.'))
		csv_file.write(',')
		if len(row['zipcode'])!=0:
			csv_file.write((row['zipcode'][0]).encode('utf-8').strip(' ,.'))
		csv_file.write(',')
		if len(row['phone'])!=0:
			csv_file.write((row['phone'][0]).encode('utf-8').strip(' ,.'))
		csv_file.write('\n')
		csv_file.close()
	return

    #Generate vCards entries from your extracted data VERSION: 3.0
    def convertToVCard(self, csv_file_name):
	reader = csv.reader(open(csv_file_name, 'rb'))
	#reader = open(csv_file_name, 'rb')
	vCards_folder = 'vCards/'
	path = str(vCards_folder) + str(self.input_item_city_region) + '/'		#Destination Folder e.g. cupcakes
	
	if not os.path.isdir(vCards_folder):
		os.mkdir(vCards_folder,0777)
   		if not os.path.isdir(path):
			os.mkdir(path,0777)
   		
	count = 0
    	for row in reader:
		count = count + 1
		vCard = open(path +str(row[0]).replace(' ', '-')+'-'+str(count)+'.vcf', 'w')
		vCard.write('BEGIN:VCARD')
		vCard.write('\n')
		vCard.write('VERSION:3.0')
		vCard.write('\n')
		vCard.write('ORG:' + row[0])
		vCard.write('\n')
		vCard.write('TEL;WORK;VOICE:' + row[5])
		vCard.write('\n')
		vCard.write('ADR;TYPE=WORK:;;' + row[1] +';' + row[2] + ';' + row[3] + ';' + row[4])
		vCard.write('\n')
		vCard.write('LABEL;TYPE=WORK:' + row[1] +'\\n' + row[2] + ',' + row[3] + ' ' + row[4])
		vCard.write('\n')
		vCard.write('REV:' + (self.local_datetime).strftime(self.fmt))
		vCard.write('\n')
		vCard.write('END:VCARD')
		vCard.close()
		
	return