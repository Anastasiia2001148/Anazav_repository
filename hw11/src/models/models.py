from sqlalchemy import Column, String, Date, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contapp'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)  # Убедитесь, что эта строка присутствует
    birthday = Column(Date)
    additional_data = Column(String)