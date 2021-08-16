from sqlalchemy import Column, Integer, String
from slack_bot_package.database import Base

class BlacklistCategory(Base):
    __tablename__ = 'blacklist_category'
    id = Column(Integer, primary_key=True)
    category_name = Column(String)

class DoneParseApp(Base):
    __tablename__ = 'done_parse_app'
    id = Column(Integer, primary_key=True)
    app_href = Column(String)
    emails = Column(String)

class FavoritesDeveloper(Base):
    __tablename__ = 'favorites_developer'
    id = Column(Integer, primary_key=True)
    dev_href = Column(String)

class TrashEmail(Base):
    __tablename__ = 'trash_emails'
    id = Column(Integer, primary_key=True)
    app_href = Column(String)
    trash_emails = Column(String)