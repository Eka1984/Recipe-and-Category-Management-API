from datetime import datetime
def get_recipes_by_category_id(cnx, category_id):
    cursor = cnx.cursor()
    _query = "SELECT * FROM recipe WHERE category_id = (%s) ORDER BY id"
    cursor.execute(_query, (category_id,))
    recipes = cursor.fetchall()
    recipes_list = []
    for recipe in recipes:
        recipes_list.append({
            'id': recipe[0],
            'name': recipe[1],
            'description': recipe[2],
            'created_at': recipe[3],
            'deleted_at': recipe[4],
            'user_id': recipe[5],
            'category_id': recipe[6],
            'state_id': recipe[7]
        })

    cursor.close()
    return recipes_list

def insert_recipe_into_category(cnx, request_data, category_id):
    user_id = 5147
    state_id = 2

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

    try:
        cursor = cnx.cursor()
        _query = ("INSERT INTO recipe(name, description, created_at, user_id, category_id, state_id) "
                  "VALUES((%s),(%s),(%s),(%s),(%s),(%s))")
        cursor.execute(_query, (request_data['name'], request_data['description'], formatted_datetime,
                                user_id, category_id, state_id))

        cnx.commit()
        new_recipe = {
            'category_id': category_id,
            'description': request_data['description'],
            'id': cursor.lastrowid,
            'name': request_data['name'],
            'state_id': state_id,
            'user_id': user_id
        }
        cursor.close()
        return new_recipe
    except Exception as e:
        cnx.rollback()
        print(e)
        raise e