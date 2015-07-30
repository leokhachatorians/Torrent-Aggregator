from torrent_class import Torrent

class Kickass(Torrent):
	def __init__(self, search_term):
		self.search_term = search_term.replace(' ', '%20')
		self.page_num = 1

		self.amount = 1
		self.lowest_value = 1

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
		self.seeds = self.bs4_grabber(soup, class_name='green center')
		self.leeches = self.bs4_grabber(soup, class_name='red lasttd center')
		self.titles = self.bs4_grabber(soup, class_name='cellMainLink')
		self.info = self.bs4_grabber(soup, class_name='nobr center')
		self.magnet_link = tree.xpath('//*[@class="imagnet icon16"]/@href')
		self.website_name = 'Kickass Torrents'

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
		url = self.create_complete_url(self.page_num, self.search_term, Kickass=True)
		r = self.create_requests(url)
		soup = self.create_soup(r, html_parser=True)
		tree = self.create_tree(r)
		self.grab_data(soup, tree)
