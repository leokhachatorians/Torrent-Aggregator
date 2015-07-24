import requests
from bs4 import BeautifulSoup
from lxml import html

class Torrent():
	# For all children of the Torrent class the initial database number
	# will ALWAYS be one, makes no sense to do it any other way.
	db_num = 1
	page_num = None
	r = None
	soup = None
	tree = None
	amount = None
	titles = None
	seeds = None
	leeches = None
	info = None
	magnet_link = None
	website_name = None

	# Used only for the websites which don't have an access to the magnet link
	# on the initial page loaded
	magnet_urls = None

	def create_complete_url(self, page_number, search_term, Pirate=False, Isohunt=False, Kickass=False):
		"""
		Arguments:
			page_number - The current page location

			search_term - The term to be searched

			[Pirate, Isohunt, Kickass] - Which url format to create

		Description:
			Creates and returns the complete url to being parsing data depending
			on which torrent website is set to 'True',
		"""
		if Isohunt:
			url = 'https://isohunt.to/torrents/?ihq={0}&Torrent_sort=seeders.desc&Torrent_page={1}'.format(
				search_term,
				page_number)
		elif Pirate:
			url = "https://thepiratebay.gd/search/{0}/{1}".format(
				search_term,
				page_number)
		elif Kickass:
			url = 'https://kat.cr/usearch/{0}/{1}'.format(
				search_term,
				page_number)

		return url

	def create_requests(self, url):
		"""
		Arguments:
			Url - The Url of which to create the requests of

		Description:
			Creates and returns a requests object of the given url
		"""
		r = requests.get(url)
		return r

	def create_soup(self, r, html_parser=False):
		"""
		Arguments:
			r - The requests object
			html_parser - Set to true in order to create the soup object with
						  an html.parser argument.

		Description:
			Creates and returns the BeautifulSoup object of the given
			requests input.
		"""
		if html_parser:
			soup = BeautifulSoup(r.text, 'html.parser')
		else:
			soup = BeautifulSoup(r.text)
		return soup

	def create_tree(self, r):
		"""
		Arguments:
			r - The requests object

		Description:
			Creates and returns the LXML HTML Tree of the given requests
			input
		"""
		tree = html.fromstring(r.text)
		return tree

	def increase_page_num(self, page_num, db_num, amount):
		"""
		Arguments:
			Page_Num - The argument which refers to the current page number,
					   this variable will also be returned back to the calling
					   class.

			Db_Num - The current database location

			Amount - The amount of which to increase the page number on
					 the url, as some sites have various url requirements on 
					 what constitutes going to the next page
		Description:
			Returns a tuple which increases the page number and
			the database number of whichever subclass of Torrent uses it.
		"""
		page_num += amount
		db_num += 1
		return (page_num, db_num)

	def decrease_page_num(self, page_num, db_num, amount, lowest_value):
		"""
		Arguments:
			Page_Num - The argument which refers to the current page number,
					   this variable will also be returned back to the calling
					   class.

			Db_Num - The current database location

			Amount - The amount of which to decrease the page number on
					 the url.

			Lowest Value - The lowest amount the page number can go, also
						   the actual first page of any search term.
		Description:
			Returns a tuple which decreases the page number and
			the database number of whichever subclass of Torrent uses it.
		"""
		if not page_num == lowest_value:
			page_num -= amount
			db_num -= 1

		return (page_num, db_num)

	def clear_data(self):
		"""
		Clears all the data garned from the page.
		"""
		self.r = None
		self.soup = None
		self.tree = None
		self.titles = None
		self.seeds = None
		self.leeches = None
		self.info = None
		self.magnet_link = None
		self.website_name = None
		self.url_to_magnet = None

	def bs4_grabber(self, the_soup, class_name=None, others=None):
		"""Parses a given BeautifulSoup thing and pulls out the text within
		the class given, className must be a string. If not a class name, using
		the others keyword can pull out various id tags and whatnot"""
		output = []

		if class_name:
			inside = the_soup.find_all(class_=class_name)
			for stuff in inside:
				output.append(stuff.text)

			return output

		else:
			inside = the_soup.find_all(others)
			for stuff in inside:
				output.append(stuff.text)

			return output
