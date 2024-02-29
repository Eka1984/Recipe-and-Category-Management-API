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


@webserver.route('/api/categories/<category_id>')
def category_handler(category_id):
    with connect_to_db() as cnx:
        try:
            category = data.categories.get_category_by_id(cnx, category_id)
            return jsonify({'category': category})
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
            req_body = request.get_json()
            print(req_body)
            return ""


    # täällä tietokanta yhteys on automaattisesti suljettu, eikä se ole enää käytössä
    # koska yield ei lopeta funktion suoritusta, vaan ainoastaan palauttaa meille yieldatun muuttujan,
    # niin kuin returnkin muttaa palaa with-lohkon suorituksen jälkeen takaisiin funktioon ja suorittaa
    # yieldin jälkeen tulevan koodin

#tämä ehto estää Flask-webserverin käynnistymisen, jos main importataan toiseen skriptiin
#webserverin on tarkoitus käynnistyä vain silloin, kun main.py suoritetaan python-kommennolla
if __name__ == '__main__':
    webserver.run(port=3000)