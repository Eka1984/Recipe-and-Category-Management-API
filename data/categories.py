
def get_categories(cnx):
    cursor = cnx.cursor()
    _query = "SELECT id, name FROM categories"
    cursor.execute(_query)
    categories = cursor.fetchall()
    categories_list = []
    for category in categories:
        categories_list.append({'id': category[0], 'name': category[1]})
    cursor.close()
    return categories_list

def get_category_by_id(cnx, category_id):
    cursor = cnx.cursor()
    _query = "SELECT id, name FROM categories WHERE id = (%s)"
    # jos tuplessa on ainoastaan yksi elementti, pitää laittaa pilkku loppuun
    cursor.execute(_query, (category_id,))
    category = cursor.fetchone()
    cursor.close()
    if category is None:
        raise Exception('category not found')

    return {'id': category[0], 'name': category[1]}
