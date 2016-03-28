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
user_1 = User(name="D Sass",
              email="dsass92103@gmail.com",
              picture_url="/static/users/vds_bwSelfPortrait.png")
session.add(user_1)
session.commit()
#-------------------------------------------------------------------------------
user_2 = User(name="R Jones",
              email="rj4095@gmail.com",
              picture_url="/static/users/Ronni-HeadShot.jpg")
session.add(user_2)
session.commit()
#===============================================================================
# Family: Dogs
family_dogs = Family(name="Dogs", description="", image_url="/static/dogs/generic_image.png", user_id=user_1.id)
session.add(family_dogs)
session.commit()
#===============================================================================
pet_1 = Pet(breed="Labrador", gender="Neuter", name="Rocky", age="12 1/2 years", description="BFF Chocolate Labrador", family_id=family_dogs.id, user_id=user_1.id, image_url="/static/dogs/rocky.JPG", special_needs= "Lots of hugs and petting. A cookie now-and-then.")

session.add(pet_1)
session.commit()

#===============================================================================
# Family: Cats
family_cats = Family(name="Cats", description="", image_url="/static/cats/generic_image.jpg", user_id=user_1.id)
session.add(family_cats)
session.commit()
#===============================================================================
pet_2 = Pet(breed="Unknown", gender="Neuter", name="Kitty", age="10+ years", description="Our first kitty.", family_id=family_cats.id, user_id=user_1.id, image_url="/static/cats/white_cat.jpg", special_needs="None")
session.add(pet_2)
session.commit()
#===============================================================================
pet_2 = Pet(breed="Unknown", gender="Neuter", name="Butchie", age="12 years", description="Skittish kitty. We found this guy in a plant nursery hiding under the plants.", family_id=family_cats.id, user_id=user_2.id, image_url="/static/cats/black_cat.jpg", special_needs="Doesn't like people. Always hiding, except for mealtime.")
session.add(pet_2)
session.commit()
#===============================================================================
# Family: Fish
family_fish = Family(name="Fish", description="",  image_url="/static/fish/generic_image.jpg", user_id=user_1.id)
session.add(family_fish)
session.commit()
#===============================================================================
pet_4 = Pet(name="Bubbles", description="Goldfish", family_id=family_fish.id, user_id=user_1.id, image_url="/static/fish/generic_image.jpg", special_needs='')
session.add(pet_4)
session.commit()
#-------------------------------------------------------------------------------
pet_N = Pet(name="Sushi", description="Goldfish", family_id=family_fish.id, user_id=user_1.id, image_url="/static/fish/generic_image.jpg", special_needs='')
session.add(pet_N)
session.commit()
#-------------------------------------------------------------------------------
pet_N = Pet(name="Casper", description="Goldfish", family_id=family_fish.id, user_id=user_1.id, image_url="/static/fish/generic_image.jpg", special_needs='')
session.add(pet_N)
session.commit()
#-------------------------------------------------------------------------------
pet_N = Pet(name="Shadow", description="Goldfish", family_id=family_fish.id, user_id=user_1.id, image_url="/static/fish/generic_image.jpg", special_needs='')
session.add(pet_N)
session.commit()
#-------------------------------------------------------------------------------
pet_N = Pet(name="Sunny", description="Goldfish", family_id=family_fish.id, user_id=user_1.id, image_url="/static/fish/generic_image.jpg", special_needs='')
session.add(pet_N)
session.commit()
#-------------------------------------------------------------------------------
pet_N = Pet(name="Comet", description="Goldfish", family_id=family_fish.id, user_id=user_1.id, image_url="/static/fish/generic_image.jpg", special_needs='')
session.add(pet_N)
session.commit()

print "The Pet Catalog database has been loaded with Pets!"

