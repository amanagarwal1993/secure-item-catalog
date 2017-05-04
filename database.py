# Creating an engine which will represent the interface to our database
from sqlalchemy import create_engine
engine = create_engine('sqlite:///catalog.db', echo=False)

# Declarative base allows us to use python classes to declare and 
## describe actual SQL tables and columns.
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Now that we have a base class, we can create tables and map them to the Base
from sqlalchemy import Table, Column, Integer, String, Float, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime    

class Category(Base):
    """
    A table of all the categories of items.
    Example: Breads, Dairy, Fruits, etc.
    """
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    time_of_creation = Column(DateTime, default=datetime.utcnow)
    
    @property
    def givejson(self):
        return {
            'id': self.id,
            'name': self.name,
            'time_of_creation': self.time_of_creation
        }

class Item(Base):
    """
    Table of items, each belonging to a category.
    """
    __tablename__ = 'item'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(140))
    available = Column(Boolean, nullable=False)
    time_of_creation = Column(DateTime, default=datetime.utcnow)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship(Category)
    user_id = Column(String(30), nullable=False)
    
    @property
    def givejson(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'category': self.category_id,
            'is_available': self.available,
            'time_of_creation': self.time_of_creation
        }

Base.metadata.create_all(engine)
