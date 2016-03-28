#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
pet_catalog_creator.py

A Pet Family:

In zoological nomenclature, the family names of animals end with the suffix "-idae".[3]

In zoology, the family as a rank intermediate between order and genus was introduced by Pierre André Latreille in his Précis des caractères génériques des insectes, disposés dans un ordre naturel (1796). He used families (some of them were not named) in some but not in all his orders of "insects" (which then included all arthropods).

Families can be used for evolutionary, palaeontological and generic studies because they are more stable than lower taxonomic levels such as genera and species.[4][5]

The most popular pets are likely dogs and cats, but people also keep house rabbits, ferrets; rodents such as gerbils, hamsters, chinchillas, fancy rats, and guinea pigs; avian pets, such as canaries, parakeets, and parrots; reptile pets, such as turtles, lizards and snakes; aquatic pets, such as goldfish, tropical fish and frogs; and arthropod pets, such as tarantulas and hermit crabs.

family:
    cats
    dogs
    rabbits
    ferrets
    rodents
        gerbil
        hamster
        chinchilla
        rat
        guinea pig
    avians
        canary
        parakeet
        parrot
    reptiles
        turtle
        lizard
    aquatics
        goldfish
        tropical fish
        frog
    arthropods
        tarantula
        hermit crab

----------------------------------------------------------------

Despite the centrality of the idea of "breeds" to animal husbandry and agriculture, no single, scientifically accepted definition of the term exists.[1] A breed is therefore not an objective or biologically verifiable classification but is instead a term of art amongst groups of breeders who share a consensus around what qualities make some members of a given species members of a nameable subset.[2]

'''
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

DB_NAME = "pet_catalog.db"

class User(Base):
    """
    User(Base):     Define characteristics of a User - a person who defines and
                    controls the content of the Pet Family and Pets

    Argument:       name, email, picture_url

    Return:         An initialized Family object
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=True)
    picture_url = Column(String(2048), nullable=True)

    def __init__(self, name='', email='', picture_url=''):
        self.name = name
        self.email = email
        self.picture_url = picture_url
        return

class Family(Base):
    """
    Family(Base):   Define characteristics of a Pet Family

    Argument:       name, description, image_url, user_id

    Return:         An initialized Family object
    """
    __tablename__ = 'family'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=True)
    image_url = Column(String(1024), nullable=True)

    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

    def __init__(self, name='', description='', image_url='', user_id=1):
        self.name = name
        self.description = description
        self.image_url = image_url
        self.user_id = user_id
        return

    @property
    def serialize(self):
        """
        serialize(self):    Return object data in easily serializeable format
        """
        return {'name'          : self.name,
                'id'            : self.id,
                'user_id'       : self.user_id,
                'description'   : self.description,
                'image_url'     : self.image_url
        }
 
class Pet(Base):
    """
    Pet(Base):  Define characteristics of a Pet

    Argument:   name, description, image_url, user_id, breed,
                gender, age, special_needs, family_id, user_id

    Return:     An initialized Pet object
    """
    __tablename__ = 'pet'

    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    description = Column(String(250), nullable=True)
    image_url = Column(String(1024), nullable=True)

    breed =  Column(String(25), nullable=True)
    gender =  Column(String(9), nullable=True)
    age =  Column(String(5), nullable=True)
    special_needs = Column(String(1024), nullable=True)

    family_id = Column(Integer,ForeignKey('family.id'))
    family = relationship(Family)

    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

    def __init__(self, name='', description='', image_url='', breed='',
                 gender='', age='', special_needs='', family_id=1, user_id=1):
        self.name = name
        self.description = description
        self.image_url = image_url

        self.breed = breed
        self.gender = gender
        self.age = age
        self.special_needs = special_needs

        self.family_id = family_id
        self.user_id = user_id
        return

    @property
    def serialize(self):
        """
        serialize(self):    Return object data in easily serializeable format
        """
        return {
                'id'           : self.id,
                'user_id'      : self.user_id,
                'name'         : self.name,
                'breed'        : self.breed,
                'gender'       : self.gender,
                'age'          : self.age,
                'special_needs': self.special_needs,
                'description'  : self.description,
                'image_url'    : self.image_url
            }

engine = create_engine("sqlite:///{}".format(DB_NAME))
Base.metadata.create_all(engine)
