from torrent_class import Torrent

class Isohunt(Torrent):
	def __init__(self, search_term):
		self.search_term = search_term.replace(' ', '+')
		self.page_num = 0

		self.amount = 40
		self.lowest_value = 40

	def grab_data(self, soup=None, tree=None):
		self.titles = tree.xpath("//*[@class='title-row']/a/span/text()")
		self.seeds = tree.xpath("//*[@class=' sy']/text()")
		self.leeches = ''
		self.info = tree.xpath("//*[@class='size-row']/text()")
		self.website_name = 'Isohunt'
		self.magnet_urls = tree.xpath("//*[@id='serps']/table/tbody/tr/td[2]/a/@href")

	def get_magnet(self, url_to_magnet):
		url_to_magnet = 'https://isohunt.to' + url_to_magnet
		r = requests.get(url_to_magnet)
		tree = r.text
		return tree.xpath("//*[@class='btn btn-lg btn-warning btn-magnet btn-border-left']/@href")

	def start(self):
		url = self.create_complete_url(self.page_num, self.search_term, Isohunt=True)
		r = self.create_requests(url)
		soup = self.create_soup(r)
		tree = self.create_tree(r)
		self.grab_data(soup, tree)
