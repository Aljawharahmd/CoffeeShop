import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
        drinks = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
        }), 200

    except:
        abort(404)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        drinks = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drink': drinks
        }), 200
    except:
        abort(404)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):

    body = request.get_json()

    if not ('title' in body and 'recipe' in body):
        abort(422)
    
    try:
        title = body.get('title')
        recipe = body.get('recipe')

        drink = Drink(title=title, recipe=json.dumps(recipe))

        drink.insert()

        drink = Drink.query.filter_by(title=title).first()
        return jsonify({
            'success': True,
            'drinks': drink.long()
            #'drinks': [drink.long()]
        }), 200
    except:
        abort(500)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):

    drink = Drink.query.filter_by(id=id).first()
    
    if not drink:
        abort(404)

    try:
        body = request.get_json()

        title = body.get('title')
        recipe = body.get('recipe')

        if title:
            drink.title = title
        if recipe:
            drink.title = recipe

        drink.update()  
            
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    
    drink = Drink.query.filter_by(id=id).first()

    if not drink:
        abort(404)

    try:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        }), 200
    except:
        abort(422)


# Error Handling
@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        'success':False,
        'error':400,
        'message':'Bad request'
    }), 400

@app.errorhandler(404)
def notfound(error):
    return jsonify({
        'success':False,
        'error':404,
        'message':'Resource not found'
    }), 404

@app.errorhandler(405)
def unprocessable(error):
    return jsonify({
        'success':False,
        'error':405,
        'message':'Method not allowed'
    }), 405

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success':False,
        'error':422,
        'message':'Unprocessable entity'
    }), 422

@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
        'success':False,
        'error':500,
        'message':'Internal server error'
    }), 500

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code



    