from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CategoryItem

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category App"

# connect to database and create database session
engine = create_engine('sqlite:///catalogappwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Show catalog
@app.route('/')
@app.route('/catalog/')
def show_catalog():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(CategoryItem).order_by(desc(CategoryItem.id)).limit(10)
    return render_template('catalog.html', categories=categories, items=items)


@app.route('/catalog.json')
def get_catalog():
    categories = session.query(Category).order_by(asc(Category.name))
    my_list = []
    for category in categories:
        items = session.query(CategoryItem).filter_by(category_id=category.id).all()
        json_post = {
            'id': category.id,
            'name': category.name,
            'Item': [item.serialize for item in items]
        }
        my_list.append(json_post)

    return jsonify(Category=my_list)


# create a new category
@app.route('/catalog/new/', methods=['GET', 'POST'])
def new_category():
    if request.method == 'POST':
        category = Category(name=request.form['name'])
        session.add(category)
        flash('New category %s Successfully Created' % category.name)
        session.commit()
        return redirect(url_for('show_catalog'))
    else:
        return render_template('newcategory.html')


# show a category
@app.route('/catalog/<int:category_id>/')
@app.route('/catalog/<int:category_id>/items/')
def show_category(category_id):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem).filter_by(category_id=category_id).all()

    return render_template('category.html', items=items, category=category, categories=categories)


@app.route('/catalog/<string:category_name>/<string:item_name>/view')
def show_category_item(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()

    item = session.query(CategoryItem).filter_by(category_id=category.id, title=item_name).one()
    can_edit = can_user_edit(item)

    return render_template('showcategoryitem.html', item=item, can_edit=can_edit)


def can_user_edit(item):
    user_id = login_session.get('user_id')
    can_edit = False
    if user_id is not None and user_id == item.user_id:
        can_edit = True
    return can_edit


@app.route('/catalog/item/new', methods=['GET','POST'])
def add_category_item():
    return new_category_item(None)


@app.route('/catalog/<string:category_name>/item/new', methods=['GET','POST'])
def new_category_item(category_name):
    if request.method == 'POST':
        user_id = login_session['user_id']
        category_id = request.form['category_id']
        category = session.query(Category).filter_by(id=category_id).one()
        new_item = CategoryItem(title=request.form['name'], description=request.form['description'],
                               category_id=category.id, user_id=user_id)
        session.add(new_item)
        session.commit()

        flash('New Category Item %s Successfully Created' % (new_item.title))
        return render_template('showcategoryitem.html', item=new_item, can_edit=True)
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('newcategoryitem.html', category_name=category_name, categories=categories)


@app.route('/catalog/<string:item_name>/<int:item_id>/edit', methods=['GET','POST'])
def edit_category_item(item_name, item_id):
    edited_item = session.query(CategoryItem).filter_by(id=item_id).one()
    user_id = login_session['user_id']

    if user_id is not None and user_id == edited_item.user_id:
        if request.method == 'POST':
            if request.form['name']:
                edited_item.title = request.form['name']
            if request.form['description']:
                edited_item.description = request.form['description']
            if request.form['category_id']:
                new_category_id = request.form['category_id']
                if edited_item.category_id != new_category_id:
                    new_category = session.query(Category).filter_by(id=new_category_id).one()
                    edited_item.category = new_category
                    edited_item.category_id = new_category_id

            session.add(edited_item)
            session.commit()

            flash('Catalog Item: %s, successfully updated' % (edited_item.title))
            return show_category(edited_item.category_id)
        else:
            categories = session.query(Category).order_by(asc(Category.name))
            return render_template('editcategoryitem.html', item=edited_item, categories=categories, can_edit=True)
    else:
        flash('You cannot change the Catalog Item: %s' % (item_name))
        return render_template('showcategoryitem.html', item=edited_item, can_edit=False)


@app.route('/catalog/<string:item_name>/<int:item_id>/delete', methods=['GET','POST'])
def delete_category_item(item_name, item_id):
    item_to_delete = session.query(CategoryItem).filter_by(id=item_id).one()
    user_id = login_session['user_id']
    if user_id is not None and user_id == item_to_delete.user_id:
        if request.method == 'POST':
            session.delete(item_to_delete)
            session.commit()

            flash('Catalog Item: %s, successfully deleted' % (item_to_delete.title))
            return show_category(item_to_delete.category_id)
        else:
            return render_template('deletecategoryitem.html', item=item_to_delete, can_edit=True)
    else:
        flash('You cannot change the Catalog Item: %s' % (item_name))
        return render_template('showcategoryitem.html', item=item_to_delete, can_edit=False)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    # Exchange client token for long lived server-side token with GET /oauth/
    # access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret
    # ={app_secret}&fb_exchange_token={short-lived-token}
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s" \
          "&client_secret=%s&fb_exchange_token=%s" % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.11/me"

    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.11/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.11/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: ' + \
              ' 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must be included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    response = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        print "Failed to upgrade the authorization code."
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
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

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        print "Token's client ID does not match app's"
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    print " glpus_id %s " % gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # Add provider to login session
    login_session['provider'] = 'google'
    user_id = get_user_id(data["email"])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: ' + \
              ' 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route("/gdisconnect")
def gdisconnect():
    # Only disconnect a connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# User Helper Functions

def create_user(login_session):
    new_user = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook_id':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('show_catalog'))
    else:
        flash("You were not logged in to begin with!")
        return redirect(url_for('show_catalog'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

