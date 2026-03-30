from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'
    id = Column(Integer, primary_key=True)
    subject = Column(String)
    body = Column(String)
    recipient = Column(String)

# Database connection setup (example)
engine = create_engine('sqlite:///emails.db')
Base.metadata.create_all(engine)