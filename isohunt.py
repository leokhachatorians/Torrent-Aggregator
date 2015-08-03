from torrent_class import Torrent

class Isohunt(Torrent):
	def __init__(self, search_term):
		self.search_term = search_term.replace(' ', '+')
		self.page_num = 0

		self.amount = 40
		self.lowest_value = 40

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
		self.titles = tree.xpath("//*[@class='title-row']/a/span/text()")
		self.seeds = tree.xpath("//*[@class=' sy']/text()")
		self.leeches = ''
		self.info = tree.xpath("//*[@class='size-row']/text()")
		self.website_name = 'Isohunt'
		self.magnet_urls = tree.xpath("//*[@id='serps']/table/tbody/tr/td[2]/a/@href")

	def get_magnet(self, url_to_magnet):
		"""
		Arguments:
			url_to_magnet - String containing the url of the
					torrent's main page
		Description:
			Isohunt does not display magnet link info when parsing
			the search results, so when a user attempts to download
			retrieve the parsed URL for the torrent page,
			create a requests object, a html.tree object,
			and then parse the tree for the location of the magnet link
		"""
		url_to_magnet = 'https://isohunt.to' + url_to_magnet
		r = requests.get(url_to_magnet)
		tree = r.text
		return tree.xpath("//*[@class='btn btn-lg btn-warning btn-magnet btn-border-left']/@href")

	def start(self):
		"""
		Description:
			1) Loads the page
			2) Creates the requests objects
			3) Creates the tree object
			4) Begins the process of grabbing data
			
			Will look to refactor this to make it so
			each step is its own function, but it does
		
		url = self.create_complete_url(self.page_num, self.search_term, Isohunt=True)
		r = self.create_requests(url)
		soup = self.create_soup(r)
		tree = self.create_tree(r)
		self.grab_data(soup, tree)
