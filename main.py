from isohunt import Isohunt
from kickass import Kickass
from pirate import Piratebay
import webbrowser
import sys
from db import session, Torrents
from PyQt4 import QtCore, QtGui, uic

main_page = uic.loadUiType("pages/main_page.ui")[0]

class MainWindow(QtGui.QMainWindow, main_page):
	"""Defines and creates the main window"""

	def __init__(self, parent=None):
		QtGui.QMainWindow.__init__(self, parent)
		self.setupUi(self)

		# Set up button actions
		self.search_btn.clicked.connect(self.search)
		self.next_page_btn.clicked.connect(self.next_page)
		self.prev_page_btn.clicked.connect(self.previous_page)

		# Set up file menu actions
		self.action_exit.triggered.connect(self.close)

		# Set up torrent site data holders
		self.pirate = None
		self.kickass = None
		self.isohunt = None

		# Variables which will determine which websites to parse through
		self.parse_pirate = False
		self.parse_kickass = False
		self.parse_isohunt = False

		# The current page location, used to track what page the user is currently on
		# Used for the forward/backward functionality on the GUI
		self.page_num = 1

		# Default next/previous page states set to disabled to prevent weird glitches
		self.set_page_buttons_state(state=False)

		# Set up context menu for manager
		self.manager.customContextMenuRequested.connect(
			self.context_menu_for_manager)

	def context_menu_for_manager(self, event):
		"""
		Creates the right click functionality for the actual password manger.
		"""
		self.menu = QtGui.QMenu(self)

		# Download Torrent
		action_download = QtGui.QAction('Download Torrent', self)
		action_download.triggered.connect(self.download_torrent)
		self.menu.addAction(action_download)

		self.menu.popup(QtGui.QCursor.pos())

	def download_torrent(self):
		"""
		Description:
			When the user right clicks on a valid cell, parse through the database
			for the matching instance. Once the instance has been selected, either 
			create a new page to retrieve the magnet url if the torrent selected is 
			from isohunt, or just open the magnet link using python default webbrowser
			if the link was available during the initial parsing.
		"""
		row = self.manager.currentRow()
		title = self.manager.item(row, 0).text()
		seed = self.manager.item(row, 1).text()

		for instance in session.query(Torrents).filter_by(title=title, seeds=seed):
			# Check to determine if the selection is isohunt, as isohunt does not have
			# a magnet link on the initial search page we need to load the magnet link from
			# the actual torrent page
			if instance.magnet_link == 'None':
				magnet = self.isohunt.get_magnet(instance.url)
				webbrowser.open_new_tab(magnet)
			else:
				webbrowser.open_new_tab(instance.magnet_link)

	def create_classes(self, search_term):
		"""
		Arguments:
			search_term - The search term inputted by the user
		Description:
			Create and initialize new instances of all three classes using the
			search term. Creating all the classes at once has no significant performance
			problems as the majority of the work is done when attempting to parse the
			pages.
		"""
		self.pirate = Piratebay(search_term)
		self.kickass = Kickass(search_term)
		self.isohunt = Isohunt(search_term)

	def run_classes(self, parse_pirate=False, parse_kickass=False, parse_isohunt=False):
		"""
		Arguments:
			parse_pirate - Boolean parameter
			parse_kickass - Boolean parameter
			parse_isohunt - Boolean parameter
		Description:
			Data retrieval will begin depending on what websites the users wishes to retireve
			and parse for. Setting the values from their default state of false to true will
			ensure that those and those only will be the ones which data will be retrieved for.
		"""
		if parse_pirate:
			self.pirate.start()
		if parse_kickass:
			self.kickass.start()
		if parse_isohunt:
			self.isohunt.start()

	def search(self):
		"""
		Description:
			Whenever a user clicks the search button there a few steps taken to ensure
			clean data retrieval. 
			1] Determine if the search term is valid or not
			2] The database has the contents of its tables dumped, as to ensure that there
				is no cross contamination of other previous queries.
			3] Re-create the classes with the newly desired search term.
			4] Collect and set which websites the user would like to search through
			5] Run the classes which the user previously selected
			6] Add the data retrieved to the database, ensuring that only the sites
				selected are the sites which actually add data
			7] Populate the manager and present it to the user
		"""
		if self.check_if_empty_string(self.search_term.text()):
			QtGui.QMessageBox.warning(
				self, "Invalid Entry", "Search Field Cannot Be Empty")
		elif self.check_if_website_selected() is False:
			QtGui.QMessageBox.warning(
				self, "Invalid Entry", "Select Atleast One Website")
		else:
			self.dump_table()
			self.create_classes(self.search_term.text())
			self.check_which_websites()
			self.run_classes(parse_isohunt=self.parse_isohunt,
							 parse_kickass=self.parse_kickass,
							 parse_pirate=self.parse_pirate)
			self.add_to_db(parse_pirate=self.parse_pirate,
						   parse_kickass=self.parse_kickass,
						   parse_isohunt=self.parse_isohunt)
			self.populate_manager(self.page_num)
			self.set_page_buttons_state(state=True)

	def clear_manager(self, amount=0):
		# Always sets the rowcount to zero first, otherwise first row acts weird
		self.manager.setRowCount(0)
		self.manager.setRowCount(amount)

	def next_page(self):
		"""
		Description:
			Loads the next page of all the websites selected.

			Note that even though all the websites may have not been
			selected, we simultaneously increase the page number and
			the databse number of not only the GUI but also all of the
			torrent classes. This way, if the user wishes to add any additional
			sites to parse, they can be on the same page as they would have been
			if originally selected.
		"""
		self.page_num += 1
		self.pirate.clear_data()
		self.kickass.clear_data()
		self.isohunt.clear_data()

		self.pirate.page_num, self.pirate.db_num = self.pirate.increase_page_num(
													self.pirate.page_num, 
													self.pirate.db_num, 
													self.pirate.amount)

		self.kickass.page_num, self.kickass.db_num = self.kickass.increase_page_num(
													self.kickass.page_num, 
													self.kickass.db_num, 
													self.kickass.amount)

		self.isohunt.page_num, self.isohunt.db_num = self.isohunt.increase_page_num(
													self.isohunt.page_num, 
													self.isohunt.db_num, 
													self.isohunt.amount)
		self.clear_manager(1)

		if session.query(Torrents).filter_by(page_number=self.page_num).count() >= 1:
			self.populate_manager(self.page_num)
		else:
			self.run_classes()
			self.add_to_db(parse_pirate=self.parse_pirate,
						   parse_kickass=self.parse_kickass,
						   parse_isohunt=self.parse_isohunt)
			self.populate_manager(self.page_num)

	def previous_page(self):
		"""
		Description:
			Loads the previous page of all torrent websites selected
			from the database and displays it back to the user.

			Note that even though all the websites may have not been
			selected, we simultaneously decrease the page number and
			the databse number of not only the GUI but also all of the
			torrent classes. This way, if the user wishes to add any additional
			sites to parse, they can be on the same page as they would have been
			if originally selected.
		"""
		self.pirate.clear_data()
		self.kickass.clear_data()
		self.isohunt.clear_data()
		if self.page_num == 1:
			self.page_num = 1
		else:
			self.page_num -= 1

			self.pirate.page_num, self.pirate.db_num = self.pirate.decrease_page_num(
														self.pirate.page_num,
														self.pirate.db_num,
														self.pirate.amount,
														self.pirate.lowest_value)

			self.kickass.page_num, self.kickass.db_num = self.kickass.decrease_page_num(
														self.kickass.page_num,
														self.kickass.db_num,
														self.kickass.amount,
														self.kickass.lowest_value)

			self.isohunt.page_num, self.isohunt.db_num = self.isohunt.decrease_page_num(
														self.isohunt.page_num,
														self.isohunt.db_num,
														self.isohunt.amount,
														self.isohunt.lowest_value)
		self.clear_manager(1)
		self.populate_manager(self.page_num)

	def dump_table(self):
		"""
		Description:
			Removes all data within the Torrents table
		"""
		session.query(Torrents).delete()

	def set_page_buttons_state(self, state=False):
		"""
		Arguments:
			state - Boolean value
		Description:
			Based on what state is passed, either enable the next page
			and previous page buttons or disable them.
		"""
		if state:
			self.prev_page_btn.setEnabled(True)
			self.next_page_btn.setEnabled(True)
		else:
			self.prev_page_btn.setEnabled(False)
			self.next_page_btn.setEnabled(False)

	def add_to_db(self, parse_pirate=False, parse_kickass=False, parse_isohunt=False):
		"""
		Arguments:
			parse_pirate - Boolean parameter
			parse_isohunt - Boolean parameter
			parse_kickass - Boolean parameter
		Description:
			Given the choices of what the user selected to retrieve data for,
			append all the data found into the database.
		"""
		if parse_pirate:
			for i in range(len(self.pirate.titles)):
				session.add(Torrents(
					title=self.pirate.titles[i],
					seeds=self.pirate.seeds[i],
					leech=self.pirate.leeches[i],
					info=self.pirate.info[i],
					website=self.pirate.website_name,
					magnet_link=self.pirate.magnet_link[i],
					page_number=self.pirate.db_num
				))
			session.commit()

		if parse_kickass:
			for i in range(len(self.kickass.titles)):
				session.add(Torrents(
					title=self.kickass.titles[i],
					seeds=self.kickass.seeds[i],
					leech=self.kickass.leeches[i],
					info=self.kickass.info[i],
					website=self.kickass.website_name,
					magnet_link=self.kickass.magnet_link[i],
					page_number=self.kickass.db_num
				))
			session.commit()

		if parse_isohunt:
			for i in range(len(self.isohunt.titles)):
				session.add(Torrents(
					title=self.isohunt.titles[i],
					seeds=self.isohunt.seeds[i],
					leech=self.isohunt.leeches,
					info=self.isohunt.info[i],
					website=self.isohunt.website_name,
					page_number=self.isohunt.db_num,
					magnet_link='None',
					magnet_urls=self.isohunt.magnet_urls[i]))
				session.commit();

	def populate_manager(self, page_num):
		"""
		Arguments:
			page_num - The page location of all the torrent classes, set by the GUI
		Description:
			Given a page number, retrieve all data within the database which has the same
			page number as the GUI and display that information to the user.
		"""
		row = 0
		item = 0
		limit = session.query(Torrents).count()

		self.manager.setRowCount(0)
		self.manager.setRowCount(1)

		for instance in session.query(Torrents).order_by(Torrents.seeds.desc()).filter_by(page_number=page_num):
			self.manager.setItem(row, item, QtGui.QTableWidgetItem(instance.title))
			item += 1
			self.manager.setItem(row, item, QtGui.QTableWidgetItem(str(instance.seeds)))
			item += 1
			self.manager.setItem(row, item, QtGui.QTableWidgetItem(str(instance.leech)))
			item += 1
			self.manager.setItem(row, item, QtGui.QTableWidgetItem(instance.info))
			item += 1
			self.manager.setItem(row, item, QtGui.QTableWidgetItem(instance.website))
			item = 0

			if row < limit - 1:
				row += 1
				self.manager.insertRow(row)

		self.manager.resizeColumnsToContents()

	def check_which_websites(self):
		"""
		Description:
			Check which websites the user would like to parse. Then set
			the values.
		"""
		if self.check_box_isohunt.isChecked():
			self.parse_isohunt = True
		else:
			self.parse_isohunt = False
		if self.check_box_pirate.isChecked():
			self.parse_pirate = True
		else:
			self.parse_pirate = False
		if self.check_box_kickass.isChecked():
			self.parse_kickass = True
		else:
			self.parse_kickass = False

	def check_if_website_selected(self):
		"""
		Description:
			Checks to see if any websites were selected
		"""
		if not self.parse_kickass and not self.parse_pirate and not self.parse_isohunt:
			return False

	def check_if_empty_string(self, search_term):
		"""
		Description:
			Takes in the search term and determines if the string is empty
		"""
		if not search_term or not search_term.strip():
			return True

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	gui = MainWindow()
	gui.show()
	app.exec_()
