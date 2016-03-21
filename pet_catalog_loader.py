#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
pet_catalog_loader.py


'''
from os import remove
from sys import exit
from time import sleep

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from pet_catalog_creator import Base, Family, Pet, User

DB_NAME = "pet_catalog.db"

#try:
#    remove(db_name)
#except OSError:
#    sys.exit("OSError removing {}".format(db_name))

engine = create_engine('sqlite:///{}'.format(DB_NAME))

# sleep(5)


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

#===============================================================================
# Users
user_1 = User(name="Dennis Sass", email="dsass92103@gmail.com")
session.add(user_1)
session.commit()
#-------------------------------------------------------------------------------
user_2 = User(name="Tommy John", email="tj@gmail.com")
session.add(user_2)
session.commit()
#===============================================================================
# Family: Dogs
family_dogs = Family(name="Dogs", user = user_1)
session.add(family_dogs)
session.commit()
#===============================================================================
pet_1 = Pet(breed="TBD", gender="TBD", name="Rocky", age="TBD", description="BFF Chocolate Labrador", family=family_dogs, user=user_1, image_url="file:///C:.\static\dogs\dog_rocky.jpg", special_needs= "TBD")

session.add(pet_1)
session.commit()
#===============================================================================
# Family: Cats
family_cats = Family(name="Cats", user=user_1)
session.add(family_cats)
session.commit()
#===============================================================================
pet_2 = Pet(breed="TBD", gender="TBD", name="Kitty", age="TBD", description="Our first kitty. Lost her right front leg in an accident.", family=family_cats, user=user_1, image_url="TBD", special_needs="TBD")
session.add(pet_2)
session.commit()
#===============================================================================
# Family: Gerbil
family_3 = Family(name="Gerbil", user=user_1)
session.add(family_3)
session.commit()
#===============================================================================
pet_3 = Pet(name="PeeWee", description="Funny-looking animal...", family=family_3, user=user_1, image_url="TBD", special_needs='')
session.add(pet_3)
session.commit()
#===============================================================================
# Family: Fish
family_fish = Family(name="Fish", user=user_1)
session.add(family_fish)
session.commit()
#===============================================================================
pet_4 = Pet(name="Bubbles", description="Goldfish", family=family_fish, user=user_1, image_url="TBD", special_needs='')
session.add(pet_4)
session.commit()
#===============================================================================
# Family: Pig
family_5 = Family(name="Pig", user=user_1)
session.add(family_5)
session.commit()
#===============================================================================
pet_5 = Pet(name="Tubby", description="Pig", family=family_5, user=user_1, image_url="TBD", special_needs='')
session.add(pet_5)
session.commit()
#-------------------------------------------------------------------------------
pet_N = Pet(name="Sushi", description="Goldfish", family=family_fish, user=user_1, image_url="TBD", special_needs='')
session.add(pet_N)
session.commit()
#-------------------------------------------------------------------------------
pet_N = Pet(name="Casper", description="Goldfish", family=family_fish, user=user_1, image_url="TBD", special_needs='')
session.add(pet_N)
session.commit()
#-------------------------------------------------------------------------------
pet_N = Pet(name="Shadow", description="Goldfish", family=family_fish, user=user_1, image_url="TBD", special_needs='')
session.add(pet_N)
session.commit()
#-------------------------------------------------------------------------------
pet_N = Pet(name="Sunny", description="Goldfish", family=family_fish, user=user_1, image_url="TBD", special_needs='')
session.add(pet_N)
session.commit()
#-------------------------------------------------------------------------------
pet_N = Pet(name="Comet", description="Goldfish", family=family_fish, user=user_1, image_url="TBD", special_needs='')
session.add(pet_N)
session.commit()
#-------------------------------------------------------------------------------
pet_N = Pet(name="Butchie", description="Found this guy in a plant nursery hiding under the plants.", family=family_cats, user=user_1, image_url="TBD", special_needs='')
session.add(pet_N)
session.commit()


print "The Pet Catalog database has been loaded with Pets!"

