from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///my-sqlite.db", echo=True)
Session = sessionmaker(bind=engine)

Base = declarative_base()
