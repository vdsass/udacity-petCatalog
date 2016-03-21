#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
pet_catalog_server.py


'''
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from pet_catalog_creator import Base, Family, Pet, User
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

_DEBUG = True

CLIENT_ID = json.loads(
    open('gplus_client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Pet Catalog"
DB_NAME = "pet_catalog.db"

# Connect to Database and create database session
engine = create_engine('sqlite:///{}'.format(DB_NAME))
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login/')
def showLogin():
    '''
    showLogin() - create a 'random' state variable and display the login prompts via html

    Arguments: None

    Return: render the login HTML page; returns to TODO

    '''
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if _DEBUG:
        print
        print "gconnect(): request.args.get('state')={}".format(request.args.get('state'))
        print "gconnect(): login_session['state']={}".format(login_session['state'])

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data
    if _DEBUG:
        print "gconnect(): [authorization] code={}".format(code)

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('gplus_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)


        if _DEBUG:
            for cred in credentials:
                print "gconnect(): cred={}".format(cred)




    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify access token
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))

    if _DEBUG:
        print "gconnect(): url={}".format(url)

    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if _DEBUG:
        print "gconnect(): result['user_id']={}".format(result['user_id'])
        print "gconnect(): gplus_id={}".format(gplus_id)

    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        #print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id    = login_session.get('gplus_id')

    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is currently connected.'),200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    if _DEBUG:
        print "gconnect(): login_session['provider']= {}".format(login_session['provider'])
        print "gconnect(): login_session['access_token']= {}".format(login_session['access_token'])
        print "gconnect(): login_session['gplus_id']= {}".format(login_session['gplus_id'])

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print "gconnect(): data={}".format(data)

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']


    # verify user is registered
    user_id = getUserID(login_session['email'])
    if user_id is not None:
        user_info = getUserInfo(user_id)
        login_session['user_id'] = user_id

        if _DEBUG:
            print "gconnect(): User is registered! user_id={}".format(user_id)
            print "gconnect(): user_info={}".format(user_info)

    else:
        new_user_id = createUser(login_session)
        login_session['user_id'] = new_user_id

        if _DEBUG:
            print "gconnect(): User is not Registered!"
            print "gconnect(): new_user_id={}".format(new_user_id)


    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are logged in as {}".format(login_session['username']))

    if _DEBUG:
        print "Fini!"
        print

    return output

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    access_token = request.data
    print "fbconnect(): [authorization] code={}".format(access_token)

    app_id = json.loads(open('fb_client_secrets.json','r').read())['app']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json','r').read())['app']['app_secret']

    url = "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s" % (app_id,app_secret,access_token)

    h = httplib2.Http()
    result = h.request(url,'GET')[1]

    # use token to get user infor from API
    userinfo_url = "https://graph.facebook.com/v2.2/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token

    if _DEBUG:
        print "url sent for API access:()".format(url)

    h = httplib2.Http()
    result = h.request(url,'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # get user picture
    url = "https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200".format(token)

    h = httplib2.Http()
    result = h.request(url,'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id= getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are logged in as {}".format(login_session['username']))

    if _DEBUG:
        print "Fini!"
        print

    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    for login_session_item in login_session:
        print 'gdisconnect(): login_session_item= {}'.format(login_session_item)

    access_token = login_session['access_token']
    print "gdisconnect(): login_session['username']= {}".format(login_session['username'])
    print "gdisconnect(): login_session['access_token']= {}".format(login_session['access_token'])

    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(access_token)
    print "gdisconnect(): url={}".format(url)

    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'gdisconnect(): result= {}'.format(result)

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = "https://graph.facebook.com/{}/permissions?access_token={}".format(facebook_id,access_token)

    if _DEBUG:
        print "fbdisconnect(): facebook_id={}".format(facebook_id)
        print "fbdisconnect(): access_token={}".format(access_token)
        print "fbdisconnect(): url={}".format(url)

    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return

@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully logged out.")
    else:
        flash("You are not logged in.")

    return redirect(url_for('showFamilies'))

#
# JavaScript Object Notation (json) APIs to view Family and Pet information
#
@app.route('/family/<int:family_id>/pets/json/')
def petsJSON(family_id):
    '''
    petsJSON(family_id) - json list of individual pet entries that match the Family id (i.e., Dog)

    Argument: family_id

    Return: 'jsonified' version of information for Pets in a Family
    '''

    pets = session.query(Pet).filter_by(family_id=family_id).all()

    if _DEBUG:
        for pet in pets:
            print
            print "pet.id = {}".format(pet.id)
            print "\tpet.breed = {}".format(pet.breed)
            print "\tpet.name = {}".format(pet.name)
            print

    return jsonify(Pet_Information = [pet.serialize for pet in pets])

@app.route('/families/json/')
def familiesJSON():
    '''
    familiesJSON() - json list of individual pet family entries

    Argument: None

    Return: 'jsonified' version of information for Pet Families
    '''

    families = session.query(Family).all()

    if _DEBUG:
        for family in families:
            print
            print "family.id = {}".format(family.id)
            print "\tfamily.name = {}".format(family.name)
            print

    return jsonify(Family_Information = [family.serialize for family in families])

# Show all pet families
@app.route('/')
@app.route('/families/')
def showFamilies():

    families = session.query(Family).order_by(asc(Family.name))

    # if user is not logged-in, allow viewing...
    #  ... but no create, update, or delete actions
    if 'username' not in login_session:
        return render_template('public_families.html', families=families)
    else:
        # if user is logged-in allow CRUD activity
        return render_template('families.html', families=families)


# Create a new pet Family
@app.route('/family/new/', methods=['GET', 'POST'])
def newFamily():

    if 'username' not in login_session:
        return redirect('/login/')

    if request.method == 'POST':
        newFamily = Family(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newFamily)
        flash("New Family (category) {} Successfully Created".format(newFamily.name))
        session.commit()
        return redirect(url_for("showFamilies"))
    else:
        return render_template("newFamily.html")

# Edit a Family dB entry
@app.route('/family/<int:family_id>/edit/', methods=['GET', 'POST'])
def editFamily(family_id):

    if 'username' not in login_session:
        return redirect('/login/')

    familyToEdit = session.query(Family).filter_by(id=family_id).one()

    if familyToEdit.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this pet family. Please create your own pet family to edit.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        if request.form['name']:
            family.name = request.form['name']
            flash('Family Successfully Edited {}'.format(family.name))
            return redirect(url_for('showFamilies'))
    else:
        return render_template('editFamily.html', family_id=family_id)


# Delete a Family entry
@app.route('/family/<int:family_id>/delete/', methods=['GET', 'POST'])
def deleteFamily(family_id):

    if 'username' not in login_session:
        return redirect('/login/')

    families = session.query(Family).order_by(asc(Family.name))
    familyEntryToDelete = session.query(Family).filter_by(id=family_id).one()

    if familyEntryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this Family entry. Please create your own Family to delete.');}</script><body onload='myFunction()'>"

    if request.method == 'POST':
        session.delete(familyEntryToDelete)
        session.commit()
        flash('{} Successfully Deleted'.format(familyEntryToDelete.name))
        return redirect(url_for('showFamilies', families=families))
    else:
        return render_template('deleteFamily.html', family=familyEntryToDelete)

# Show a list of all Pets in a Family
#  (i.e., Family=Dogs, Pet=Sasha, Pet=Jake, ...)
@app.route('/family/<int:family_id>/pets/')
def showPets(family_id):

    family = session.query(Family).filter_by(id=family_id).one()
    pets = session.query(Pet).filter_by(family_id=family.id).all()
    creator = getUserInfo(family.user_id)

    if _DEBUG:
        print
        print "showPets(): family={}".format(family)
        print "showPets(): creator={}".format(creator)
        print
        for pet in pets:
            print "pet.id = {}".format(pet.id)
            print "\tpet.breed = {}".format(pet.breed)
            print "\tpet.name = {}".format(pet.name)
            print "\tpet.gender = {}".format(pet.gender)
            print "\tpet.age = {}".format(pet.age)
            print "\tpet.description = {}".format(pet.description)
            print
    '''
    In order to view the profile picture of the creator of each menu, add code to your project.py file to query the creator:

    creator = getUserInfo(pet.user_id)

    then pass in the creator object when you render the template:

    return render_template('publicmenu.html', items = items, pet = pet, creator= creator)

    Inside your templates you can now use {{creator.picture}}} and {{creator.username}} to share the name and picture of each pet creator.
    '''

    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('public_pets.html', family=family, pets=pets, creator=creator)
    else:
        return render_template('pets.html', family=family, pets=pets, creator=creator)


# Create a new menu item
@app.route('/family/<int:family_id>/pets/new/', methods=['GET', 'POST'])
def newPet(family_id):
    if 'username' not in login_session:
        return redirect('/login/')

    pet = session.query(Family).filter_by(id=family_id).one()

    if pet.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to create this pet''s menus. Please create your own pet in order to create new menus.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'], description=request.form['description'], family_id=family_id, user_id=family.user_id)
        session.add(newItem)
        session.commit()
        flash('Pet {} Successfully Created'.format(pet.name))
        return redirect(url_for('showPets', pet_id=pet_id))
    else:
        return render_template('newPet.html', family_id=family_id)

# Edit a Pet
@app.route('/family/<int:family_id>/pets/<int:pet_id>/edit/', methods=['GET', 'POST'])
def editPet(family_id, pet_id):
    if 'username' not in login_session:
        return redirect('/login/')

    editPet = session.query(Pet).filter_by(id=pet_id).one()

    if editPet.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this pet. Please create your own pet to edit.');}</script><body onload='myFunction()''>"

    editedPet = session.query(Pet).filter_by(id=pet_id).one()

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']

        session.add(editedPet)
        session.commit()

        flash('Pet Successfully Edited')
        return redirect(url_for('showPets', pet_id=pet_id))
    else:
        return render_template('editPet.html', family_id=family_id, pet_id=pet_id, pet=editedPet)


# Delete a Pet
@app.route('/family/<int:family_id>/pets/<int:pet_id>/delete/', methods=['GET', 'POST'])
def deletePet(family_id, pet_id):

    if 'username' not in login_session:
        return redirect('/login/')

    #petFamily = session.query(Family).filter_by(id=family_id).all()
    petToDelete = session.query(Pets).filter_by(id=pet_id).one()

    if petToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this pet. Please create your own pet to delete.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        session.delete(petToDelete)
        session.commit()
        flash('Pet Successfully Deleted')
        return redirect(url_for('showPets', family_id=petToDelete.family_id))
    else:
        return render_template('deletePet.html', pet=petToDelete)

def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user


def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
