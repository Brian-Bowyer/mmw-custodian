from databases import Database
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from app.constants import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
database = Database(DATABASE_URL)
