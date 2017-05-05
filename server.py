from flask import Flask, render_template, request
from flask import redirect, url_for, abort, flash, jsonify
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Category, Item
from urllib import quote
import uuid
import requests
import json
import random
import string
# Supporting functions for checking inputs
from supporting import *

app = Flask('__main__')
app.secret_key = str(uuid.uuid4())

engine = create_engine('sqlite:///catalog.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()


# Main Page
@app.route('/')
def main():
    if 'user_id' in login_session:
        signin = 'Logout'
    else:
        signin = 'Login'
    categories = session.query(Category).all()
    if len(categories) > 0:
        found = True
    else:
        found = False
    return render_template('main.html', categories=categories, 
                           found=found, signin=signin)


# Json endpoint for main page
@app.route('/json')
def mainjson():
    categories = session.query(Category).all()
    return jsonify(grocery_categories=[category.givejson for category in categories])


@app.route('/login/', methods=['GET', 'POST'])
def login():
    global previous_url
    if request.method == 'GET':
        previous_url = request.referrer
        if 'user_id' in login_session:
            flash('You are already logged in. \
            Log out if you want to login as someone else.')
            return redirect(url_for('main'))
        return render_template('login.html', error=None)

    if request.method == 'POST':
        if 'user_id' in login_session:
            # Already logged in
            flash('You are already logged in. \
            Log out if you want to login as someone else.')
            return previous_url
        else:
            # Get client id from file and log the user in
            CLIENT_ID = json.loads(
                open('client_secrets.json', 'r').read()
            )['web']['client_id']
            # Receive data from ajax request by browser
            data = request.get_json()
            token = data['token']
            # Url endpoint for verifying users securely through google
            token_url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=' 
                         + token)
            r = requests.get(token_url)
            reply = r.json() # dictionary object
            
            # validCreds is in the supporting.py file
            if validCreds(reply, CLIENT_ID):
                login_session['user_id'] = reply['sub']
                flash('You have been logged in!')
                return url_for('main')
            else:
                return render_template('login.html', 
                                       error='Problem in authentication.')


@app.route('/logout/')
def logout():
    # Logs out not only from server but also from client
    login_session.pop('user_id', None)
    return redirect(url_for('main'))


# Page for each category
@app.route('/categories/<category_name>/')
def categoryPage(category_name):
    category = session.query(Category).filter_by(
        name=category_name.capitalize()).first()
    if 'user_id' in login_session:
        signin = 'Logout'
    else:
        signin = 'Login'
    if category is not None:
        # category exists
        try:
            items = session.query(Item).filter_by(
                category_id = category.id).all()
            if len(items) > 0:
                # Success
                category_found = True
                items_found = True
            else:
                category_found=True
                items_found=False
                items = []
        except:
            # Fail: Items not found
            category_found=True
            items_found=False
            items = []
    else:
        # Category not found, fake request
        return categoryNotFound(category_name, 
                                template='category.html', 
                                signin=signin)
    return render_template('category.html', 
                           category_found=category_found, 
                           items_found=items_found, 
                           items=items, 
                           category=category, 
                           signin=signin)


# Json endpoint for category page
@app.route('/categories/<category_name>/json')
def categoryjson(category_name):
    category = session.query(Category).filter_by(
        name=category_name.capitalize()).first()
    if category is not None:
        # category exists
        try:
            items = session.query(Item).filter_by(
                category_id = category.id).all()
            if len(items) > 0:
                # Success
                return jsonify(items=[item.givejson for item in items])
            else:
                return jsonify(items=[])
        except:
            # Fail: Items not found
            return jsonify(items=[])
    else:
        # Category not found
        return 'Category not found'


# Page for each item of a category
@app.route('/categories/<category_name>/<int:item_id>/')
def itemsPage(category_name, item_id):
    category = session.query(Category).filter_by(
        name=category_name.capitalize()).first()
    if 'user_id' in login_session:
        signin = 'Logout'
    else:
        signin = 'Login'
    if category is not None:
        try:
            item = session.query(Item).filter_by(id=item_id).one()
            # Success
            if item.category_id == category.id:
                category_found=True
                item_found=True
                return render_template('item.html', 
                                        category_found=True,
                                        item_found=True,
                                        category=category,
                                        item=item, 
                                        signin=signin)
            else:
                #Failure: Item doesn't match category, fake request
                return itemNotFound(category=category, 
                                    template='item.html', 
                                    signin=signin)
        except:
            # Error while querying item, or item doesn't exist
            return itemNotFound(category=category, 
                                template='item.html', 
                                signin=signin)
    else:
        # Category doesn't exist, fake/bad request
        return categoryNotFound(category_name, 
                                template='item.html', 
                                signin=signin)


# Json endpoint for item page
@app.route('/categories/<category_name>/<int:item_id>/json')
def itemjson(category_name, item_id):
    category = session.query(Category).filter_by(
        name=category_name.capitalize()).first()
    if category is not None:
        # category exists
        try:
            item = session.query(Item).filter_by(id=item_id).one()
            if item.category_id == category.id:
                # Success
                return jsonify(item=item.givejson)
            else:
                return 'Error while finding item'
        except:
            # Fail: Item not found
            return 'Error while finding item'
    else:
        # Category not found
        return 'Category not found'


@app.route('/<category_name>/<int:item_id>/edit/', 
           methods=['GET', 'POST'])
def editItem(category_name, item_id):
    # Check for user authentication first
    if 'user_id' in login_session:
        signin = 'Logout'
    else:
        signin = 'Login'
        flash('You must be logged in to edit this item.')
        return redirect(url_for('itemsPage', 
                                category_name=category_name, 
                                item_id=item_id))
    category = session.query(Category).filter_by(
        name=category_name.capitalize()).first()
    if category is not None:
        # Check beforehand if category and item exist, if not, return error immediately
        try:
            item = session.query(Item).filter_by(
                id=item_id).one()
            if item.category_id == category.id:
                if (login_session['user_id'] == item.user_id):
                    #If item does exist and is in category, render edit page with form.
                    if request.method == 'GET':
                        # Render form with values pre-filled with item details.
                        return render_template('edit_item.html', 
                                               category=category, 
                                               item=item, 
                                               signin=signin)
                    if request.method == 'POST':
                        #Check if form details are legit, otherwise keep rendering edit form.
                        availability = request.form['availability']
                        if availability == "Yes":
                            avail = True
                        if availability == "No":
                            avail = False
                        (everything_alright, errors, critical_error) = checkFormInputs(request, category_name)
                        # Fake form, because categories of url and post request don't match.
                        if critical_error:
                            flash('Something went wrong. Try again.')
                            return redirect(url_for('itemsPage', 
                                                    category_name=category.name, item_id=item.id))
                        if everything_alright:
                            # Update the item and send it back to database.
                            item.name = request.form['item_name']
                            item.price = request.form['item_price']
                            item.available = avail
                            item.description = request.form['item_description']
                            session.add(item)
                            session.commit()
                            # Reload item page with new details
                            return redirect(url_for('itemsPage', 
                                                    category_name=category.name, item_id=item.id))
                        else:
                            return render_template('edit_item.html', 
                                                    category=category, 
                                                    signin=signin,
                                                    errors = errors)
                else:
                    # User not authorized
                    flash('You can only edit an item if you created it yourself!')
                    return redirect(url_for('itemsPage', 
                                            category_name=category.name, 
                                            item_id=item.id))
            else:
                # Item not found in category
                return itemNotFound(category=category, 
                                    template='item.html', 
                                    signin=signin)
        except:
            # Error finding item
            return itemNotFound(category=category, 
                                template='item.html', 
                                signin=signin)
    else:
        # Category doesn't exist
        return categoryNotFound(category_name, 
                                'item.html', 
                                signin=signin)


@app.route('/<category_name>/<int:item_id>/delete/', 
           methods=['GET', 'POST'])
def deleteItem(category_name, item_id):
    # Check for user login
    if 'user_id' in login_session:
        signin = 'Logout'
    else:
        signin = 'Login'
        flash('You must be logged in to edit or delete this item.')
        return redirect(url_for('itemsPage', 
                                category_name=category_name, 
                                item_id=item_id))
    category = session.query(Category).filter_by(
        name=category_name.capitalize()).first()
    if category is not None:
        try:
            item = session.query(Item).filter_by(id=item_id).one()
            # Item if sound and belongs to same category
            if item.category_id == category.id:
                if login_session['user_id'] == item.user_id:
                    #If item does exist and is in category, render edit page with form.
                    if request.method == 'GET':
                        # Render form with values pre-filled with item details.
                        return render_template('delete_item.html', 
                                               category=category, 
                                               item=item, 
                                               signin=signin)
                    if request.method == 'POST':
                        #If form is legit, update the item and send it back to database. Reload item page with new details.
                        session.delete(item)
                        session.commit()
                        return redirect(url_for('categoryPage', 
                                                category_name=category.name))
                else:
                    # User not authorized
                    flash('You can only delete an item if you created it yourself!')
                    return redirect(url_for('itemsPage', 
                                            category_name=category.name, 
                                            item_id=item.id))
            else:
                # Item not found in category
                return itemNotFound(category=category, 
                                    template='item.html', 
                                    signin=signin)
        except:
            # Error finding item
            return itemNotFound(category=category, 
                                template='item.html', 
                                signin=signin)
    else:
        # Category doesn't exist
        return categoryNotFound(category_name, 
                                'item.html', 
                                signin=signin)


@app.route('/<category_name>/new/', methods=['GET', 'POST'])
def newItem(category_name):
    # Check for authentication
    if 'user_id' in login_session:
        signin = 'Logout'
    else:
        signin = 'Login'
        flash('You must be logged in to create a new item.')
        return redirect(url_for('categoryPage', 
                                category_name=category.name))
    category = session.query(Category).filter_by(
        name=category_name.capitalize()).first()
    if category is not None:
        if request.method == 'GET':
            return render_template('add_item.html', 
                                    category_found=True, 
                                    category=category, 
                                    signin=signin)
        if request.method == 'POST':
            #Check if form details are legit, otherwise keep rendering edit form.
            availability = request.form['availability']
            if availability == "Yes":
                avail = True
            elif availability == "No":
                avail = False
            (everything_alright, errors, critical_error) = checkFormInputs(request, category_name)
            # Fake form, because categories of url and post request don't match.
            if critical_error:
                flash('Something went wrong. Try again.')
                return redirect(url_for('categoryPage', 
                                        category_name=category_name))
            if everything_alright:
                new_item = Item(name = request.form['item_name'],
                            price = request.form['item_price'],
                            available = avail,
                            description = request.form['item_description'],
                            category_id = category.id, 
                            user_id = login_session['user_id'])
                # Update the item and send it back to database.
                session.add(new_item)
                session.commit()
                # Reload item page with new details
                return redirect(url_for('itemsPage', 
                                        category_name=category.name, 
                                        item_id=new_item.id))
            else:
                return render_template('add_item.html', 
                                        category=category, 
                                        signin=signin,
                                        errors = errors)
    else:
        return render_template('add_item.html', 
                               category_found=False, 
                               fault=category_name, 
                               signin=signin)

@app.errorhandler(404)
def page_not_found(e):
    return 'Error 404<br><br><br> \
    Something went <em>terribly, terribly</em> wrong. \
    Check url again. :)'

# RUNNING THE APP
app.debug = 1
app.run(host='0.0.0.0', port=5000)