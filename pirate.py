from torrent_class import Torrent

class Piratebay(Torrent):
	def __init__(self, search_term):
		self.search_term = search_term.replace(' ', '%20')
		self.page_num = 1

		# Amount of how much to increase the page_num by
		self.amount = 1
		self.lowest_value = 0

	def grab_data(self, soup=None, tree=None):
		"""
		Arguments:
			soup - The beautiful soup object of the page
			tree - the lxml object of the page
		Description:
			Depending on the easiest way to parse for data,
			uses bs4 or lxml. Has a custom function 'bs4_grabber'
			for all beautiful objects.
		"""
		self.titles = self.bs4_grabber(soup, class_name='detLink')
		self.info = tree.xpath('//*[@id="searchResult"]/tr/td[2]/font/text()')

		# Must remove to ensure that if 'anonymous' is the uploader, then it won't crash, doesn't properly parse otherwise
		self.info = [i.replace(', ULed by ', '') for i in self.info]

		self.seeds = tree.xpath('//*[@id="searchResult"]/tr/td[3]/text()')
		self.leeches = tree.xpath('//*[@id="searchResult"]/tr/td[4]/text()')
		self.magnet_link = tree.xpath('//*[@id="searchResult"]/tr/td[2]/a[1]/@href')
		self.website_name = 'The Pirate Bay'

	def start(self):
		"""
		Description:
			1) Loads the page
			2) Creates the requests objects
			3) Creates the tree object
			4) Begins the process of grabbing data
			
			Will look to refactor this to make it so
			each step is its own function, but it does
			make things more tidy having it in one method.
		"""
		url = self.create_complete_url(self.page_num, self.search_term, Pirate=True)
		r = self.create_requests(url)
		soup = self.create_soup(r)
		tree = self.create_tree(r)
		self.grab_data(soup, tree)
