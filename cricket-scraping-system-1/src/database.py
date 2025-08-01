from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import json

Base = declarative_base()

class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer, Sequence('match_id_seq'), primary_key=True)
    title = Column(String(255))
    date = Column(String(50))
    score = Column(String(50))

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/cricket_data.db')

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def get_session():
    return Session()

def add_match(title, date, score):
    session = get_session()
    new_match = Match(title=title, date=date, score=score)
    session.add(new_match)
    session.commit()
    session.close()

def get_all_matches():
    session = get_session()
    matches = session.query(Match).all()
    session.close()
    return matches

def clear_matches():
    session = get_session()
    session.query(Match).delete()
    session.commit()
    session.close()