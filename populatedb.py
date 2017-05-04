from sqlalchemy import create_engine
engine = create_engine('sqlite:///catalog.db', echo=True)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

from database import Category, Item

breads = Category(name='Breads')
dairy = Category(name='Dairy')
veggies = Category(name='Vegetables')
poultry = Category(name='Poultry')
fruits = Category(name='Fruits')
cereal = Category(name='Cereal')
jam = Category(name='Jams')
sauce = Category(name='Sauces')
flour = Category(name='Flour')
spices = Category(name='Spices')
poultry = Category(name='Poultry')
beans = Category(name='Beans')
tea = Category(name='Tea')
coffee = Category(name='Coffee')

cats = []
cats.extend([breads, dairy, veggies, 
             poultry, fruits, cereal, 
             jam, sauce, flour, spices, 
             poultry, beans, tea, coffee])

session.add_all(cats)
session.commit()