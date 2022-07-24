from .auth.auth import AuthError, requires_auth
from .database.models import db_drop_and_create_all, setup_db, Drink
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

@app.route('/', methods=['GET'])
def home():
    """Home Route"""
    return jsonify({
        'success': True,
        'message': "Home Route"
    })

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
    """Get all drinks, permissible to all"""

    try:
        drink_queryset = Drink.query

        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drink_queryset]
        })
    except:
        abort(500)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drink-details')
def get_drink_details():
    try:
        drink_queryset = Drink.query

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drink_queryset]
        })
    except:
        abort(500)


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
@requires_auth('post:drink')
def create_drink():
    """Create a drink"""

    body = request.get_json()

    recipe = body.get('recipe', None)
    title = body.get('title', None)

    if not recipe or not title: abort(400)

    try:
        drink = Drink(
            title=title,
            recipe=json.dumps(recipe)
        )

        drink.insert()

        return jsonify({
            'success': True,
            'created': drink.long()
        }), 201
    except:
        abort(422)


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
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('update:drink')
def update_drink(id):
    """Update a drink"""

    data = request.get_json()
    if not data: abort (400)

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink: abort(404)

    if 'title' in data:
        drink.title = data['title']

    if 'recipe' in data:
        drink.recipe = json.dumps(data['recipe'])

    try:
        drink.update()

        return jsonify({
            'success': True,
            'data': drink.long()
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
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('del:drink')
def delete_drink(id):
    """Delete a drink"""

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink: abort(404)

    try:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': id
        }), 200
    except:
        abort(500)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                "success": False,
                "error": 404,
                "message": "resource not found"
                }), 404

'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request',
    }), 400

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found',
    }), 404

@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed',
    }), 405

@app.errorhandler(500)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error',
    }), 500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized',
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'Forbidden',
    }), 403

@app.errorhandler(AuthError)
def process_AuthError(error):
    response = jsonify(error.error)
    response.status_code = error.status_code

    return response


if __name__ == "__main__":
    app.debug = True
    app.run()
