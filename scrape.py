# Jeff Stern, dedicated to Cait Holman
# Scrapes http://apod.nasa.gov/apod/ and downloads all photos

from bs4 import BeautifulSoup
from urllib import FancyURLopener

import urllib2
import os
import re
import csv
import sys
import datetime

def parse_html(url):
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	content = response.read()
	return BeautifulSoup(content, "html.parser")

def get_current_date_string():
	return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")

def get_images(site):
	media = site.find("div","media")
	images = []
	if media:
		images = media.find_all("img")
		photoset = media.find("iframe","photoset")
		if photoset:
			photosetPage = parse_html(photoset['src'])
			images = images + photosetPage.find_all("img")
	return images

def get_copy(site):
	return site.find("div","copy")

def convert_to_plain_text(copy):
	return copy.text

def get_all_attr(elementList, attr):
	return [a[attr] for a in elementList]

def get_tags(site):
	tags = site.find("dl","tags")
	if tags:
		return [a.text for a in tags.find_all("a")]
	else:
		return []

def download_photo(img_url, filename):
	# http://stackoverflow.com/questions/3042757/downloading-a-picture-via-urllib-and-python
	try:
	    image_on_web = urllib2.urlopen(img_url)
	    if image_on_web.headers.maintype == 'image':
	        buf = image_on_web.read()
	        path = os.getcwd() + "/"
	        file_path = "%s%s" % (path, filename)
	        downloaded_image = file(file_path, "wb")
	        downloaded_image.write(buf)
	        downloaded_image.close()
	        image_on_web.close()
	    else:
			return False    
	except:
		print("URL for "+ img_url + " not found")
		return False
	return True

def create_csv_with_metadata():
	output_file = open("collecteddata_"+get_current_date_string()+".csv", 'wb')
	output = csv.writer(output_file)
	output.writerow(["URL", "Text", "Links", "Image URLS", "Image Alt Text","Tags"])

	for line in open("urllist.txt", 'r'):	
		try:
			site = parse_html(line)
			copy = get_copy(site)
			copyText = ""
			copyLinksHref = []
			if copy:
				copyText = convert_to_plain_text(copy)
				copyLinksHref = get_all_attr(copy.find_all("a"), "href")
			tags = get_tags(site)
			images = get_images(site)
			if images:
				imagesSrc = get_all_attr(images, "src")
				imagesAlt = get_all_attr(images, "alt")

			data = [line, copyText, copyLinksHref, imagesSrc, imagesAlt,tags]
			output.writerow([unicode(s).encode("utf-8") for s in data])

			print(line)
		except:
			print("Failed - likely because of special character in URL")
			print(line)
			sys.exit(0)

	output_file.close()

#create_csv_with_metadata()

lineNumber = 0
for line in open("urllist.txt", 'r'):
	site = parse_html(line)
	images = get_images(site)
	imageNumber = 0
	if images:
		imagesSrc = get_all_attr(images, "src")
		for src in imagesSrc:
			fileExtension = src[src.rfind("."):]
			fileName =  "post"+str(lineNumber)+"_image"+str(imageNumber) + fileExtension
			download_photo(src, fileName)
			imageNumber += 1
	lineNumber +=1

