# /* ------------------------------------------------------- Imports ------------------------------------------------------- */

import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

# /* --------------------------------------------------- Application Start ------------------------------------------------- */

app = Flask(__name__)
setup_db(app)
CORS(app)


def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app) 
  

#db_drop_and_create_all()

# /* ------------------------------------------------------ Endpoints ------------------------------------------------------ */  

@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    drinks_short = [drink.short() for drink in drinks] 
    total_drinks = len(drinks)
    
    if total_drinks == 0:
        abort(400)
    
    return jsonify({
        'success': True,
        'drinks': drinks_short,
        'total_drinks': total_drinks,
        })   



@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    
    drinks = Drink.query.all()
    drinks_long = [drink.long() for drink in drinks] 
    total_drinks = len(drinks)
    
    if total_drinks == 0:
        abort(400)
    
    return jsonify({
        'success': True,
        'drinks': drinks_long,
        'total_drinks': total_drinks,
        })  



@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)
    
        if title is None or recipe is None:
            abort(400)

        drink = Drink(title=title, recipe=json.dumps(recipe))
        
        drink.insert()

        return jsonify({
            'success':True,
            'drinks': drink.long()
        }), 200
    
    except:
        abort(500)



@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, id):
    try:    
        drink = Drink.query.filter(Drink.id == id).first()

        if drink is None:
            abort(404)
        
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        if title is None:
            abort(400)
               
        if recipe:
            drink.recipe = json.dumps(recipe)
        
        drink.title = title

        drink.update()

        return jsonify({
            'success':True,
            'drinks': drink.long()
        }), 200

    except:
        abort(500)



@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).first()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'delete': id
        }), 200

    except:
        abort(500)


# /* ---------------------------------------------------- Error Handler ---------------------------------------------------- */  
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request',
    }), 400

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

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'unprocessable',
    }), 422

@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error',
    }), 500    

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

  # /* ---------------------------------------------------- Application End ---------------------------------------------------- */  