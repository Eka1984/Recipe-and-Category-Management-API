from flask import Flask, render_template, jsonify, request
import data.categories
from db import connect_to_db

webserver = Flask(__name__)

#http://localhost:3000/categories

@webserver.route('/categories')
def categories():
    with connect_to_db() as cnx:  # cnx on yieldattu yhteys

        try:
            categories = data.categories.get_categories(cnx)

            return render_template('categories.html', rows=categories)
        except Exception as e:
            return render_template('error.html', str(e))


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



    # täällä tietokanta yhteys on automaattisesti suljettu, eikä se ole enää käytössä
    # koska yield ei lopeta funktion suoritusta, vaan ainoastaan palauttaa meille yieldatun muuttujan,
    # niin kuin returnkin muttaa palaa with-lohkon suorituksen jälkeen takaisiin funktioon ja suorittaa
    # yieldin jälkeen tulevan koodin

#tämä ehto estää Flask-webserverin käynnistymisen, jos main importataan toiseen skriptiin
#webserverin on tarkoitus käynnistyä vain silloin, kun main.py suoritetaan python-kommennolla
if __name__ == '__main__':
    webserver.run(port=3000)