from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, CategoryItem

engine = create_engine('sqlite:///catalogappwithusers.db')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
user1 = User(name="Ravinder Rakhara", email="ravinder.rakhara@gmail.com",
             picture="")
session.add(user1)
session.commit()

# Create Catalogs
category1 = Category(name="Soccer")
session.add(category1)
session.commit()

category1 = Category(name="Basketball")
session.add(category1)
session.commit()

category1 = Category(name="Baseball")
session.add(category1)
session.commit()

category1 = Category(name="Frisbee")
session.add(category1)
session.commit()

category1 = Category(name="Snowboarding")
session.add(category1)
session.commit()

category1 = Category(name="Rock Climbing")
session.add(category1)
session.commit()


# Create Category Item
catalog_item1 = CategoryItem(title="Shinguards", description="Soccer shin guards", category_id=1, user_id=1)
session.add(catalog_item1)
session.commit()


print "added catalog items!"
