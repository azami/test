# -:- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Boolean, TEXT, DateTime, TIMESTAMP,\
        UniqueConstraint, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from config import db_config
import urllib
import datetime


MAXLEN = 200


def create_dbengine(config):
    return create_engine('%s://%s:%s@localhost/%s?charset=utf8' %
                         (config['db_connect'],
                          config['db_user'],
                          config['db_password'],
                          config['database']))

Base = declarative_base()
Session = sessionmaker()
engine = create_dbengine(db_config)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    mail = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    site = Column(String, nullable=False)
    url = Column(String, nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    novel_list = relationship('Novel', order_by='Novel.id', backref='users')

    @property
    def quoteurl(self):
        return urllib.quote(self.url)

    def __repr__(self):
        return '<Users: id:%s>' % self.id


class Novel(Base):
    __tablename__ = 'novels'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    summary = Column(TEXT, nullable=False)
    tag_edit = Column(Boolean, nullable=False, default=True)
    status = Column(Boolean, nullable=False, default=True)
    created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    updated = Column(TIMESTAMP, nullable=False)
    tag_list = relationship('Tag', order_by='Tag.tag', backref='novels',
                            lazy='joined')
    author = relationship(User, backref='novels', lazy='joined')
    UniqueConstraint(user_id, title, name='user_novel')

    @property
    def shortsummary(self):
        if len(self.summary) > MAXLEN:
            return self.summary[:MAXLEN] + u'……'
        return self.summary

    @property
    def active_tags(self):
        return [tag for tag in self.tag_list if tag.status]

    def __repr__(self):
        return '<Novels: id:%s>' % self.id


class Tag(Base):
    __tablename__ = 'tags'

    novel_id = Column(Integer, ForeignKey('novels.id'), primary_key=True)
    tag = Column(String, nullable=False, primary_key=True)
    edit = Column(Boolean, nullable=False, default=True)
    status = Column(Boolean, nullable=False, default=True)
    UniqueConstraint(novel_id, tag, name='tag_key')

    novel = relationship(Novel, backref='tags')

    def __repr__(self):
        return '<Tag: novel_id:%s tag: %s>' % (self.novel_id, self.tag)
