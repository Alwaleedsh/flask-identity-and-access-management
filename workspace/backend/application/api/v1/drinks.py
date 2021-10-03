from application import db
from application.auth.models import User
from application.models import Drink

import json
from flask import g
from flask import abort, request, jsonify
from . import bp

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

#  AUTH
#  ----------------------------------------------------------------
@auth.verify_password
def verify_password(email, password):
    # if account is not provided:
    if email == '':
        return False

    # select user:
    user = User.query.filter(
        User.email == email
    ).first()

    # if user doesn't exist:
    if user is None:
        return False
    g.current_user = user

    return user.verify_password(password)

@auth.error_handler
def unauthorized():
    response = jsonify(
        {
            "success": False, 
            "error": 401,
            "message": 'Authentication is needed to access this API.'
        }
    )
    return response, 401

#  CREATE
#  ----------------------------------------------------------------
@bp.route('/drinks', methods=['POST'])
@auth.login_required
def create_drink():
    """
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    
    return
        status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
    """
    # parse POSTed json:
    drink_created = request.get_json()
    # serialize recipe as one string:
    drink_created["recipe"] = json.dumps(drink_created["recipe"])

    error = True
    try:
        drink = Drink(**drink_created)
        # insert:
        db.session.add(drink)
        db.session.commit()
        error = False
        # prepare response:
        drink = drink.long()
    except:
        # rollback:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        abort(500, description="Failed to create new Drink")

    # format:
    response = jsonify(
        {
            "success": True,
            "drinks": [drink] 
        }
    )
    return response, 200

#  READ
#  ----------------------------------------------------------------
@bp.route('/drinks', methods=['GET'])
def get_drinks():
    """
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation

    return
        status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    """
    error = True
    try:
        # select all drinks:
        drinks = Drink.query.all()
        error = False
    except:
        error = True
    finally:
        db.session.close()

    if error:
        abort(500, description="Failed to load drinks")

    # format:
    response = jsonify(
        {
            "success": True, 
            "drinks": [drink.short() for drink in drinks],
        }
    )

    return response, 200

@bp.route('/drinks-detail', methods=['GET'])
@auth.login_required
def get_drinks_detail():
    """
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation

    return 
        status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    """
    error = True
    try:
        # select all drinks:
        drinks = Drink.query.all()
        error = False
    except:
        error = True
    finally:
        db.session.close()

    if error:
        abort(500, description="Failed to load drinks")

    # format:
    response = jsonify(
        {
            "success": True, 
            "drinks": [drink.long() for drink in drinks],
        }
    )

    return response, 200

#  PATCH
#  ----------------------------------------------------------------
@bp.route('/drinks/<int:id>', methods=['PATCH'])
@auth.login_required
def edit_drink(id):
    """
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    
    return 
        status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
    """
    # parse POSTed json:
    drink_edited = request.get_json()
    # serialize recipe as one string:
    drink_edited["recipe"] = json.dumps(drink_edited["recipe"])

    error = True
    try:
        # select:
        drink = Drink.query.get(id)
        # if resource is not found:
        if drink is None:
            abort(404, description="Drink with id={} not found".format(id))
        # update:
        drink.title = drink_edited["title"]
        drink.recipe = drink_edited["recipe"]
        # insert:
        db.session.add(drink)
        db.session.commit()
        error = False
        # prepare response:
        drink = drink.long()
    except:
        # rollback:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        abort(500, description="Failed to edit the Drink with id={}".format(id))

    # format:
    response = jsonify(
        {
            "success": True,
            "drinks": [drink] 
        }
    )
    return response, 200

#  DELETE
#  ----------------------------------------------------------------
@bp.route('/drinks/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_drink(id):
    """
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission

    return 
        status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
    """
    error = True

    try:
        # select:
        drink = Drink.query.get(id)

        # if resource is not found:
        if drink is None:
            abort(404, description="Drink with id={} not found".format(id))

        # delete:
        db.session.delete(drink)
        db.session.commit()

        error = False
    except:
        # rollback:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        abort(500, description="Failed to delete Drink with id={}".format(id))
    
    # format:
    response = jsonify(
        {
            "success": True,
            "delete": id 
        }
    )

    return response, 200