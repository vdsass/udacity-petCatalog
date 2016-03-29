#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
pet_catalog_server.py
    Fulfills project P3 requirements for Udacity Full-Stack-Developer

Revision History:
  BY       DATE     REFERENCE   DESCRIPTION
vdsass  2016-03-29   2016-001   Fix request.get_data() bug in delete_pet();
                                Change naming of def's and file dependencies to
                                conform with PEP-008.

"""
from flask import Flask, render_template, request, redirect, jsonify
from flask import make_response, url_for, flash
from flask import session as login_session

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from pet_catalog_creator import Base, Family, Pet, User

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2, json, os, random, re, requests, string

# Create a Flask application object
app = Flask(__name__)

# Define constants
_DEBUG = False

# https://developers.google.com/api-client-library/python/guide/aaa_oauth
# provides documentation and APIs to define login authorization and
# authentication parameters
CLIENT_ID = json.loads(
    open('gplus_client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Pet Catalog"
DB_NAME = "pet_catalog.db"

# Connect to a database and create a database session
engine = create_engine('sqlite:///{}'.format(DB_NAME))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Show all pet families
@app.route('/')
@app.route('/families/')
def show_families():
    """
        show_families() - Main display for the Pet Families application. Shows the Pet Families defined in the database.

        Argument: None

        Return: render_template 'families.html'for full CRUD access
                render_template 'public_families.html' for read-only access
    """
    login_status = get_login_status()

    # get list of defined Pet Families
    families = session.query(Family).order_by(asc(Family.name))

    # Generate state variable for login token exchange
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for
                    x in xrange(32))
    login_session['state'] = state

    # If user is logged in display Pet Families and Pets with create, edit, an delete capability
    # If user is not logged in display Pet Families and Pets with no add, delete, or edit capability
    if 'user_id' in login_session:
        user = get_user_info(login_session['user_id'])
        return render_template('families.html', families=families, STATE=state)
    else:
        return render_template('public_families.html', families=families, STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
        gconnect() - Google Plus login and connection logic

        Argument: None

        Return: html login welcome message
    """
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

    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        if _DEBUG:
            print "gconnect(): result['user_id']={}".format(result['user_id'])
            print "gconnect(): gplus_id={}".format(gplus_id)
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify the access token is valid for this application
    if result['issued_to'] != CLIENT_ID:
        if _DEBUG:
            print "gconnect(): result['issued_to']={}".format(result['issued_to'])
            print "gconnect(): CLIENT_ID={}".format(CLIENT_ID)
        response = make_response(
            json.dumps("Token's client ID does not match application's client ID "), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id    = login_session.get('gplus_id')

    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is currently connected.'),200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'Google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    if _DEBUG:
        print "gconnect(): login_session['provider']= {}".format(login_session['provider'])
        print "gconnect(): login_session['access_token']= {}".format(login_session['access_token'])
        print "gconnect(): login_session['gplus_id']= {}".format(login_session['gplus_id'])

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    response = requests.get(userinfo_url, params=params)

    data = response.json()

    if _DEBUG:
        print
        print "gconnect(): data={}".format(data)
        print

    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['picture_url'] = data['picture']

    # verify user is registered
    user_id = getUserID(login_session['email'])

    if user_id is not None:
        user_info = get_user_info(user_id)
        login_session['user_id'] = user_id
        if _DEBUG:
            print "gconnect(): User is registered! user_id={}".format(user_id)
            print "gconnect(): user_info={}".format(user_info)
    else:
        new_user_id = create_user(login_session)
        login_session['user_id'] = new_user_id

        if _DEBUG:
            print "gconnect(): User was not Registered!"
            print "gconnect(): new_user_id={}".format(new_user_id)

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture_url']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    if _DEBUG:
        print
        print "login_session['username'] = {}".format(login_session['username'])
        print "login_session['email'] = {}".format(login_session['email'])
        print "login_session['picture_url'] = {}".format(login_session['picture_url'])
        print

    return output

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """
        fbconnect() - Facebook login and connection logic

        Argument: None

        Return: render_template 'families.html'for full CRUD access
                render_template 'public_families.html' for read-only access
    """
    if _DEBUG:
        print
        print "login_session = {}".format(login_session)
        print "request = {}".format(request)
        print "request.data = {}".format(request.data)
        print

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    access_token = request.data

    login_session['access_token'] = access_token

    client_id = json.loads(open('fb_client_secrets.json','r').read())['app']['app_id']
    client_secret = json.loads(open('fb_client_secrets.json','r').read())['app']['app_secret']

    if _DEBUG:
        print
        print "fbconnect(): access_token={}".format(access_token)
        print "fbconnect(): client_id={}".format(client_id)
        print "fbconnect(): client_secret={}".format(client_secret)
        print

    oauth_url = "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={}&client_secret={}&fb_exchange_token={}".format(client_id,client_secret,access_token)

    if _DEBUG:
        print
        print "fbconnect(): oauth_url={}".format(oauth_url)
        print

    h = httplib2.Http()
    result = h.request(oauth_url,'GET')[1]

    if _DEBUG:
        print
        print "fbconnect(): result={}".format(result)
        print

    # use token to get user information from API
    # strip expire tag from access token
    token = result.split("&")[0]

    if _DEBUG:
        print "fbconnect(): token={}".format(token)

    userinfo_url = "https://graph.facebook.com/v2.4/me?{}&fields=name,id,email".format(token)

    if _DEBUG:
        print "fbconnect(): userinfo_url={}".format(userinfo_url)

    h = httplib2.Http()
    result = h.request(userinfo_url,'GET')[1]

    data = json.loads(result)

    if _DEBUG:
        print
        print "fbconnect(): data={}".format(data)
        print

    login_session['provider'] = 'Facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # get user picture
    picture_url = "https://graph.facebook.com/v2.4/me/picture?{}&redirect=0&height=200&width=200".format(token)

    h = httplib2.Http()
    result = h.request(picture_url,'GET')[1]
    data = json.loads(result)
    if _DEBUG:
        print "fbconnect(): picture_url data={}".format(data)

    login_session['picture_url'] = data["data"]["url"]

    # see if user exists
    user_id= getUserID(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture_url']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    if _DEBUG:
        print "Fini!"
        print

    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    """
        gdisconnect() - Google Plus logout and disconnect

        Argument: None

        Return: response string
    """
    if _DEBUG:
        for login_session_item in login_session:
            print 'gdisconnect(): login_session_item = {}'.format(login_session_item)

    access_token = login_session['access_token']

    if _DEBUG:
        print "gdisconnect(): login_session['username']= {}".format(login_session['username'])
        print "gdisconnect(): login_session['access_token']= {}".format(login_session['access_token'])

    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = "https://accounts.google.com/o/oauth2/revoke?token={}".format(access_token)

    if _DEBUG:
        print "gdisconnect(): url={}".format(url)

    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if _DEBUG:
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
    """
        fbdisconnect() - Facebook logout and disconnect

        Argument: None

        Return: redirect to home page
    """
    facebook_id = login_session['facebook_id']

    # The access token must be included to successfully logout
    access_token = login_session['access_token']
    url = "https://graph.facebook.com/{}/permissions?access_token={}".format(facebook_id,access_token)

    if _DEBUG:
        print "fbdisconnect(): facebook_id={}".format(facebook_id)
        print "fbdisconnect(): access_token={}".format(access_token)
        print "fbdisconnect(): url={}".format(url)

    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return redirect(url_for('show_families'))


@app.route('/disconnect')
def disconnect():
    """
        disconnect() - Generic logout and disconnect. Calls appropriate login provider.

        Argument: None

        Return: redirect to home page
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'Google':
            gdisconnect()
            del login_session['gplus_id']

        if login_session['provider'] == 'Facebook':
            fbdisconnect()
            del login_session['facebook_id']

        # clear anything leftover from prior login
        del login_session['username']
        del login_session['email']
        del login_session['picture_url']
        del login_session['user_id']
        del login_session['provider']

        #flash("You have successfully signed out.")

    else:
        pass
        #flash("You are not signed in.")

    return redirect(url_for('show_families'))

#
# JavaScript Object Notation (json) APIs to view Family and Pet information
#
@app.route('/family/<int:family_id>/pets/json/')
def pets_json(family_id):
    """
    pets_json(family_id) - json list of individual pet entries that match the
                            Family id (i.e., Dog)

    Argument: family_id

    Return: 'jsonified' version of information for Pets in a Family
    """

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
def families_json():
    """
    families_json() - json list of individual pet family entries

    Argument: None

    Return: 'jsonified' version of information for Pet Families
    """
    families = session.query(Family).all()

    if _DEBUG:
        for family in families:
            print
            print "family.id = {}".format(family.id)
            print "\tfamily.name = {}".format(family.name)
            print

    return jsonify(Family_Information = [family.serialize for family in families])


# Create a new pet Family
@app.route('/family/new/', methods=['GET', 'POST'])
def new_family():
    """
        new_family() - Create a new Family record in the database

        Argument: None

        Return: GET:    render template to create a new Pet Family
                POST:   redirect to home page
    """
    login_status = get_login_status()

    if 'username' not in login_session:
        return redirect('/families/')

    if request.method == 'POST':
        new_family = Family(name=request.form['name'], user_id=login_session['user_id'])
        session.add(new_family)
        flash("New Family {} Successfully Created".format(new_family.name))
        session.commit()
        return redirect(url_for("show_families"))
    else:
        return render_template("new_family.html")

# Edit a Family dB entry
@app.route('/family/<int:family_id>/edit/', methods=['GET', 'POST'])
def edit_family(family_id):
    """
        edit_family(family_id) - Edit a Family record in the database

        Argument: None

        Return: not signed in: redirect to home page
                GET:    render template to create a new Pet Family
                POST:   redirect to home page
    """
    login_status = get_login_status()

    if 'username' not in login_session:
        return redirect('/families/')

    family = session.query(Family).filter_by(id=family_id).one()

    if family.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this pet family. Please create your own pet family to edit.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        if request.form['name']:
            family.name = request.form['name']
            family.description = request.form['description']

            flash('Family Successfully Edited {}'.format(family.name))
            return redirect(url_for('show_families'))
    else:
        return render_template('edit_family.html', family=family)


# Delete a Family entry
@app.route('/family/<int:family_id>/delete/', methods=['GET', 'POST'])
def delete_family(family_id):
    """
        delete_family(family_id) - Delete the Family record in the database
                                    associated with the Family Id

        Argument: family_id

        Return: not signed in: redirect to home page
                POST: redirect to home page
                GET:  render template to delete Family record
    """
    login_status = get_login_status()

    if 'username' not in login_session:
        return redirect('/families/')

    families = session.query(Family).order_by(asc(Family.name))
    familyEntryToDelete = session.query(Family).filter_by(id=family_id).one()

    if familyEntryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this Family entry. Please create your own Family to delete.');}</script><body onload='myFunction()'>"

    if request.method == 'POST':
        session.delete(familyEntryToDelete)
        session.commit()
        flash('{} Successfully Deleted'.format(familyEntryToDelete.name))
        return redirect(url_for('show_families', families=families))
    else:
        return render_template('delete_family.html', family=familyEntryToDelete)


# Show a list of all Pets in a Family
#  (i.e., Family=Dogs, Pet=Sasha, Pet=Jake, ...)
@app.route('/family/<int:family_id>/')
@app.route('/family/<int:family_id>/pets/')
def show_pets(family_id):
    """
        show_pets(family_id) - Display a list of Pets associated with the Family Id

        Argument: family_id

        Return: render template for public Pets page
                render template for edit-able Pets page
    """
    login_status = get_login_status()

    if _DEBUG:
        print
        print "login_session = {}".format(login_session)
        print

    family = session.query(Family).filter_by(id=family_id).one()
    pets = session.query(Pet).filter_by(family_id=family.id).all()

    # get user information from the database
    creator = get_user_info(family.user_id)

    if _DEBUG:
        print
        print "show_pets(): creator.id = {}".format(creator.id)
        print "\tshow_pets(): creator.name = {}".format(creator.name)
        print "\tshow_pets(): creator.picture_url = {}".format(creator.picture_url)
        print

    if _DEBUG:
        print
        print "show_pets(): family.user_id = {}".format(family.user_id)
        print "show_pets(): creator={}".format(creator)
        print
        for pet in pets:
            print "pet.id = {}".format(pet.id)
            print "\tpet.breed = {}".format(pet.breed)
            print "\tpet.name = {}".format(pet.name)
            print "\tpet.gender = {}".format(pet.gender)
            print "\tpet.age = {}".format(pet.age)
            print "\tpet.description = {}".format(pet.description)
            print

    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('public_pets.html', family=family, pets=pets, creator=creator)
    else:
        return render_template('pets.html', family=family, pets=pets, creator=creator)


# Create a new pet
@app.route('/family/<int:family_id>/pets/new/', methods=['GET', 'POST'])
def new_pet(family_id):

    login_status = get_login_status()

    if _DEBUG:
        print
        print "new_pet(): login_session = {}".format(login_session)
        print

    if 'username' not in login_session:
        return redirect('/families/')

    family = session.query(Family).filter_by(id=family_id).one()

    if family.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to create a new pet. Please login to create new pet.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':

        if _DEBUG:
            print
            print "new_pet(): request.form[] = {}".format(request.form)
            print

            print "new_pet(): request.form.getlist('name') = {}".format(request.form.getlist('name'))[0]
            print "new_pet(): request.form.getlist('description') = {}".format(request.form.getlist('description'))[0]
            print "new_pet(): request.form.getlist('image_url') = {}".format(request.form.getlist('image_url'))[0]
            print "new_pet(): request.form.getlist('breed') = {}".format(request.form.getlist('breed'))[0]
            print "new_pet(): request.form.getlist('gender') = {}".format(request.form.getlist('gender'))[0]
            print "new_pet(): request.form.getlist('age') = {}".format(request.form.getlist('age'))[0]
            print "new_pet(): request.form.getlist('special_needs') = {}".format(request.form.getlist('special_needs'))[0]
            print "new_pet(): 'family_id' = {}".format(family.id)
            print "new_pet(): 'user_id' = {}".format(family.user_id)

        name = request.form.getlist('name')[0]
        description = request.form.getlist('description')[0]
        image_url = request.form.getlist('image_url')[0]
        breed = request.form.getlist('breed')[0]
        gender = request.form.getlist('gender')[0]
        age = request.form.getlist('age')[0]
        special_needs = request.form.getlist('special_needs')[0]
        family_id = family.id
        user_id = family.user_id

        new_pet = Pet(name,description,image_url,breed,gender,
                     age,special_needs,family_id,user_id)

        session.add(new_pet)
        session.commit()

        flash('Pet {} Successfully Created'.format(new_pet.name))
        return redirect(url_for('show_pets', family_id=family.id))
    else:
        return render_template('new_pet.html', family=family)

# Edit a Pet
@app.route('/family/<int:family_id>/pets/<int:pet_id>/edit/', methods=['GET', 'POST'])
def edit_pet(family_id, pet_id):

    login_status = get_login_status()

    if 'username' not in login_session:
        return redirect('/families/')

    petToEdit = session.query(Pet).filter_by(id=pet_id).one()

    if petToEdit.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this pet. Please create your own pet to edit.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        if request.form['name']:
            petToEdit.name = request.form['name']
        if request.form['breed']:
            petToEdit.breed = request.form['breed']
        if request.form['gender']:
            petToEdit.gender = request.form['gender']
        if request.form['age']:
            petToEdit.age = request.form['age']
        if request.form['image_url']:
            petToEdit.image_url = request.form['image_url']
        if request.form['special_needs']:
            petToEdit.special_needs = request.form['special_needs']
        if request.form['description']:
            petToEdit.description = request.form['description']
        session.add(petToEdit)
        session.commit()

        flash('Pet Successfully Edited')

        return redirect(url_for('show_pets', family_id=family_id))
    else:
        return render_template('edit_pet.html', pet=petToEdit)


# Delete a Pet
@app.route('/family/<int:family_id>/pets/<int:pet_id>/delete/', methods=['GET', 'POST'])
def delete_pet(family_id, pet_id):

    login_status = get_login_status()

    if 'username' not in login_session:
        return redirect('/families/')

    petToDelete = session.query(Pet).filter_by(id=pet_id).one()

    if petToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this pet. Please create your own pet to delete.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        session.delete(petToDelete)
        session.commit()
        flash("{} removed from the database.".format(petToDelete.name ))
        return redirect(url_for('show_pets', family_id=petToDelete.family_id))
    else:
        return render_template('delete_pet.html', family_id=petToDelete.family_id, pet=petToDelete)

def getUserID(email):
    """
        getUserID(email) - retrieve user's application-assigned id from the database

        Argument: user's email address

        Return: User id if user record exists in the database
                None if user record does not exist in the database
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def get_user_info(user_id):
    """
        get_user_info(user_id) - retrieve user data from the database

        Argument: user id

        Return: User object
    """
    user = session.query(User).filter_by(id=user_id).one()
    if _DEBUG:
        print
        print "get_user_info(user_id): user.id = {}".format(user.id)
        print "\tget_user_info(user_id): user.name = {}".format(user.name)
        print "\tget_user_info(user_id): user.picture_url = {}".format(user.picture_url)
        print
    return user


def create_user(login_session):
    """
        create_user(login_session) - create a user in the application's database

        Argument: login_session object (contains information about the user from the login resource (i.e., g+, Facebook, etc.))

        Return: User id if user record exists in the database
                None if user record does not exist in the database
    """
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture_url=login_session['picture_url'])
    session.add(newUser)
    session.commit()

    try:
        user = session.query(User).filter_by(email=login_session['email']).one()
        return user.id
    except:
        if _DEBUG:
            print "EXCEPTION!: User record not found in the database."
            print "create_user(login_session)): email = {}".format(login_session['email'])
        return None

def get_login_status():
    # persist user login status
    try:
        if login_session['username']:
            flash("You are signed in with {} as {}".\
                   format(login_session['provider'],login_session['username']))
        return True
    except:
        flash("You are not signed in")
        return False



if __name__ == '__main__':
    app.secret_key = os.urandom(64)
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
