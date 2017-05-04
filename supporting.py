# Supporting functions
from flask import render_template

def checkFormInputs(request, category_name):
    errors = []
    check = False
    critical_error = False
    
    item_name = request.form['item_name']
    item_price = float(request.form['item_price'])
    availability = request.form['availability']
    item_description = request.form['item_description']
    category_confirm = request.form['category_confirm']
    
    if len(item_name) <= 30:
        checkn = True
    else:
        checkn = False
        errors.append('Item length too long')
    
    if (isinstance(item_price, int) or isinstance(item_price, float)):
        checkp = True
    else:
        checkp = False
        errors.append('Item price is invalid')
    
    if len(item_description) < 140:
        checkd = True
    else:
        checkd = False
        errors.append('Item description is too long')
    
    if category_confirm == category_name.capitalize():
        checkc = True
    else:
        checkc = False
        critical_error = True
        
    if (checkn and checkp and checkd and checkc):
        check = True
    
    return (check, errors, critical_error)


def categoryNotFound(category_name, template, signin):
    return render_template(template, category_found=False, fault=category_name, signin=signin, item_found=False, category=None, item=None, items=[])

def itemNotFound(category, template, signin):
    return render_template(template, category_found=True, category=category, signin=signin, item_found=False, item=None, fault=None)

def validCreds(reply, CLIENT_ID):
    if ((reply['iss'] in ['accounts.google.com', 
                         'https://accounts.google.com'])
    and (reply['aud'] == CLIENT_ID)):
        return True
    else:
        return False
        
    