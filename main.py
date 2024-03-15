import jwt
from flask import Flask, render_template, jsonify, request
import data.categories
import data.recipes
import data.users
from db import connect_to_db

webserver = Flask(__name__)

#http://localhost:3000/categories

def get_db_connect(route_handler):
    def wrapper(*args, **kwargs):
        with connect_to_db() as cnx:
            return route_handler(cnx, *args, **kwargs)
    return wrapper


def require_login(route_handler):
    def wrapper(cnx, *args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header is None:
                return jsonify({'err': 'Unauthorized1'}), 401

            token_parts = auth_header.split(' ')
            if len(token_parts) != 2:
                return jsonify({'err': 'Unauthorized2'}), 401

            if token_parts[0] != 'Bearer':
                return jsonify({'err': 'Unauthorized3'}), 401

            token = token_parts[1]
            payload = jwt.decode(token, data.users.SECRET, algorithms=['HS256'])

            logged_in_user = data.users.get_logged_in_user(cnx, payload['sub'])

            return route_handler(cnx, logged_in_user, *args, **kwargs)

        except Exception as e:
            print(e)
            return jsonify({'err': 'Unauthorized4'}), 401
    return wrapper

def require_role(role_id):
    def decorator(route_handler):
        def wrapper(cnx, logged_in_user, *args, **kwargs):
            if logged_in_user['role'] == role_id:
                return route_handler(cnx, logged_in_user, *args, **kwargs)
            return jsonify({'err': 'Forbidden'}), 403

        return wrapper
    return decorator

@webserver.route('/api/account')
@get_db_connect
@require_login
def get_account(cnx, logged_in_user):
    return jsonify({'account': logged_in_user})

    # with connect_to_db() as cnx:
    #     try:
    #         auth_header = request.headers.get('Authorization')
    #         if auth_header is None:
    #             return jsonify({'err': 'Unauthorized'}), 401
    #
    #         token_parts = auth_header.split(' ')
    #         if len(token_parts) != 2:
    #             return jsonify({'err': 'Unauthorized'}), 401
    #
    #         if token_parts[0] != 'Bearer':
    #             return jsonify({'err': 'Unauthorized'}), 401
    #
    #         token = token_parts[1]
    #         payload = jwt.decode(token, data.users.SECRET, algorithms=['HS256'])
    #
    #         cursor = cnx.cursor()
    #         cursor.execute('SELECT id, username, auth_role_id FROM users WHERE access_jti = (%s)', (payload['sub'],))
    #         account = cursor.fetchone()
    #         if account is None:
    #             return jsonify({'err': 'Unauthorized'}), 401
    #         return {'account': {'id': account[0], 'username': account[1], 'role_id': account[2]}}
    #
    #
    #     except Exception as e:
    #         return jsonify({'err': str(e)})


@webserver.route('/categories')
def categories():
    with connect_to_db() as cnx:  # cnx on yieldattu yhteys

        try:
            categories = data.categories.get_categories(cnx)

            return render_template('categories.html', rows=categories)
        except Exception as e:
            return render_template('error.html', str(e))

@webserver.route('/api/login', methods=['POST'])
def login():
    with connect_to_db() as cnx:
        try:
            req_body = request.get_json()
            access_token = data.users.login(cnx, req_body)
            return jsonify({'access_token': access_token})
        except Exception as e:
            return jsonify({'err': str(e)}), 500

@webserver.route('/api/register', methods=['POST'])
def register():
    with connect_to_db() as cnx:
        try:
            req_body = request.get_json()
            user = data.users.register(cnx, req_body)
            return jsonify(user)
        except Exception as e:
            return jsonify({'err': str(e)}), 500

@webserver.route('/api/users/<user_id>', methods=['DELETE'], endpoint='delete_user')
# tämä on yksi tapa tehdä pythonissa ns. dependency injection
@get_db_connect
@require_login
@require_role(4)
def delete_user(cnx, logged_in_user, user_id):
    try:
        data.users.remove_user_by_id(cnx, user_id)
        return ""
    except Exception as e:
        return jsonify({'err': str(e)}), 500

@webserver.route('/api/categories/<category_id>', methods=['GET', 'PUT', 'DELETE'])
def category_handler(category_id):
    with connect_to_db() as cnx:
        if request.method == 'GET':
            try:
                category = data.categories.get_category_by_id(cnx, category_id)
                return jsonify({'category': category})
            except Exception as e:
                return jsonify({'err': str(e)}), 404

        elif request.method == 'PUT':
            try:
                req_body = request.get_json()
                category = data.categories.get_category_by_id(cnx, category_id)
                data.categories.update_category_by_id(cnx, category, req_body)
                return jsonify({'category': {
                    'id': category['id'],
                    'name': req_body['name']
                }})
            except Exception as e:
                return jsonify({'err': str(e)}), 404
        elif request.method == 'DELETE':
            try:
                affected_rows = data.categories.delete_category_by_id(cnx, category_id)
                if affected_rows == 0:
                    return jsonify({'err': 'category not found'}), 404
                return "", 200
            except Exception as e:
                return jsonify({'err': str(e)}), 404

@webserver.route('/api/categories', methods=['POST', 'GET'])
def categories_handler():

    # with blokkia voidaan käyttääm koska käytämme contextlib.contextmanager-dekoraattoria
    # db-tiedoston connect_to_db-funktion yläpuolella
    with connect_to_db() as cnx: # cnx on yieldattu yhteys

        #tämä on muutos, joka laitetaan githubiin

        if request.method == 'GET':

            try:
                categories = data.categories.get_categories(cnx)
                return categories
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        elif request.method == 'POST':
            try:
                req_body = request.get_json()
                category = data.categories.insert_category(cnx, req_body)
                return jsonify(category)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

@webserver.route('/api/categories/<category_id>/recipes', methods=['POST', 'GET'])
def recipes_handler(category_id):

    with connect_to_db() as cnx:

        if request.method == 'GET':
            try:
                recipes = data.recipes.get_recipes_by_category_id(cnx, category_id)
                return recipes
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        elif request.method == 'POST':
            try:
                req_body = request.get_json()
                category = data.recipes.insert_recipe_into_category(cnx, req_body, category_id)
                return jsonify(category)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

@webserver.route('/api/recipes/<recipe_id>', methods=['GET', 'PUT', 'DELETE'])
def recipe_handler(recipe_id):
    with connect_to_db() as cnx:
        if request.method == 'GET':
            try:
                recipe = data.recipes.get_recipe_by_id(cnx, recipe_id)
                return jsonify({'recipe': recipe})
            except Exception as e:
                return jsonify({'err': str(e)}), 404

        elif request.method == 'PUT':
            try:
                req_body = request.get_json()
                recipe = data.recipes.get_recipe_by_id(cnx, recipe_id)
                data.recipes.update_recipe_by_id(cnx, recipe, req_body)
                return jsonify({'recipe': {
                    'id': recipe['id'],
                    'name': req_body['name'],
                    'description': req_body['description']
                }})
            except Exception as e:
                return jsonify({'err': str(e)}), 404
        elif request.method == 'DELETE':
            try:
                affected_rows = data.recipes.delete_recipe_by_id(cnx, recipe_id)
                if affected_rows == 0:
                    return jsonify({'err': 'category not found'}), 404
                return "", 200
            except Exception as e:
                return jsonify({'err': str(e)}), 404



    # täällä tietokanta yhteys on automaattisesti suljettu, eikä se ole enää käytössä
    # koska yield ei lopeta funktion suoritusta, vaan ainoastaan palauttaa meille yieldatun muuttujan,
    # niin kuin returnkin muttaa palaa with-lohkon suorituksen jälkeen takaisiin funktioon ja suorittaa
    # yieldin jälkeen tulevan koodin

#tämä ehto estää Flask-webserverin käynnistymisen, jos main importataan toiseen skriptiin
#webserverin on tarkoitus käynnistyä vain silloin, kun main.py suoritetaan python-kommennolla
if __name__ == '__main__':
    webserver.run(port=3000)