# -:- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, SmallInteger, Date, BigInteger,\
        UniqueConstraint
from config import logdb_config
import db

engine = db.create_dbengine(logdb_config)


class InLog(db.Base):
    __tablename__ = 'in_log'

    user_id = Column(Integer)
    date = Column(Date, primary_key=True, nullable=False)
    ua = Column(String, primary_key=True, nullable=False)
    ip = Column(String, primary_key=True, nullable=False)
    refer = Column(String, nullable=False)
    UniqueConstraint(date, ua, ip, refer, name='in_key')

    def __repr__(self):
        return '<InLog: date:%s>' % self.date


class OutLog(db.Base):
    __tablename__ = 'out_log'

    user_id = Column(Integer)
    novel_id = Column(Integer, nullable=False)
    date = Column(Date, primary_key=True, nullable=False)
    ua = Column(String, primary_key=True, nullable=False)
    ip = Column(String, primary_key=True, nullable=False)
    url = Column(String, nullable=False)
    refer = Column(String, nullable=False)
    UniqueConstraint(date, ua, ip, novel_id, name='out_key')

    def __repr__(self):
        return '<OutLog: date:%s>' % self.date


class NovelLog(db.Base):
    __tablename__ = 'novel_log'

    novel_id = Column(Integer, nullable=False, primary_key=True, unique=True)
    total_in = Column(BigInteger, nullable=False, default=0)
    total_out = Column(BigInteger, nullable=False, default=0)
    monthly_in = Column(Integer, nullable=False, default=0)
    monthly_out = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return '<NovelLog: id:%s>' % self.novel_id
