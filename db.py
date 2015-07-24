from sqlalchemy import create_engine, Column, Integer, String, Sequence, update, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite://')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Torrents(Base):
	__tablename__ = 'locker'

	id = Column(Integer, Sequence('website_id_seq'), primary_key=True)
	title = Column(String(140))
	seeds = Column(Integer)
	leech = Column(Integer)
	info = Column(String(140))
	website = Column(String(140))
	magnet_link = Column(Text)
	page_number = Column(Integer)
	magnet_urls = Column(String(180))

	def __repr__(self):
		return "<Website(title={}, seeds={}, leech={}, info={}, website={}, magnet_link={}, page_number={}>".format(self.title, self.seeds, self.leech, self.info, self.website, self.magnet_link, self.page_number)

# Must call to close the session before dropping the table
# Thus ensuring a clean DB after every time the app is loaded
session.commit()
Base.metadata.drop_all(bind=engine)

Base.metadata.create_all(engine)
