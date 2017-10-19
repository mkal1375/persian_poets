import requests 
from bs4 import BeautifulSoup as Bs
from urllib import parse 

def create_soup(page_url):
	"""
	create a soup object from input url
	input : url (str)
	output : soup (soup objrect)

	"""
	root_page = requests.get(page_url)
	return BS(root_page.text,"html.parser")


def clean_list(input_list):
	"""
	1)clean scaraped data : delete [1], . . . 
	2)delete items without page
		normal items : https://fa.wikipedia.org/wiki/%D9%81%D8%B1%D8%AF%D9%88%D8%B3%DB%8C
		items without page :  https://fa.wikipedia.org/w/index.php?title=%D9%85%D8%B9%D9%86%D9%88%DB%8C%DB%8C_%D8%A8%D8%AE%D8%A7%D8%B1%D8%A7%DB%8C%DB%8C&action=edit&redlink=1
		these have 'index' in url
	input : list (soup object)
	output : list (soup object)

	todo : add numeric value 
	"""
	return [x for x in input_list if all(["[" not in x.text,'index' not in x['href']])]

def get_poet(page_url):
	"""
	get poet and scrape data : poems and personal data 
	input:	poet url (string)
	output:	poet details (tupel)
	"""
	def get_info_box(poet_soup):
		"""
		get info box : wikipedia have dirty code. somewhere used .infobox and somewhere use .vcard class
		"""
		try:
			return poet_soup.select(".vcard")
		except:
			return poet_soup.select(".infobox")

	#create soup object:
	soup = create_soup(page_url)

	#scrape data :
	describe = soup.select("mw-content-text p : nth-child(1)")
	poems = soup.select(".poem")
	info_box = get_info_box(soup)

	return (describe,poems,info_box,page_url)


#crate soup from main page:
root_soup = create_soup("https://fa.wikipedia.org/wiki/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D8%B4%D8%A7%D8%B9%D8%B1%D8%A7%D9%86_%D9%81%D8%A7%D8%B1%D8%B3%DB%8C%E2%80%8C%D8%B2%D8%A8%D8%A7%D9%86")

#scrape data from clean list by css selector 
poets_list = clean_list(root_soup.select("h2 + ul li + li a , .new , h4 + ul a"))

#crate dictonary from list: merge url and name toghether
for poet in poets_list:
	poets_dict[poet.text] = urllib.parse.urljoin("https://fa.wikipedia.org/",poet['href'])



"""todos :
	1)	get_poet function => scrape data : name , Ages , picture , poems , . . .
	2)	for loop : create dict of poets tupel
	3)	convert data to JSON
	4)	save data to redis 
"""



