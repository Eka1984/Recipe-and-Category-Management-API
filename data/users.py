import datetime
import uuid

import jwt
from passlib.hash import pbkdf2_sha512 as pl

SECRET = 'gfdgfd54353fgfdgf54gfdg5f4545dfgdf3545fgdff543dfgdfg343hte34dfggfdgd546815'

def logout(cnx, logged_in_user):
    try:
        cursor = cnx.cursor()
        _query = "UPDATE users SET access_jti = NULL WHERE id = (%s)"
        cursor.execute(_query, (logged_in_user['id'],))
        cnx.commit()
    except Exception as e:
        cnx.rollback()
        raise e

def login(cnx, req_body):
    try:
        # 1. haetaan käyttäjä userbamen perusteella
        cursor = cnx.cursor()
        cursor.execute('SELECT * FROM users WHERE username = (%s)', (req_body['username'],))
        user = cursor.fetchone()
        if user is None:
            raise Exception('user not found1')
        cursor.close()

        #2. jos käyttäjä löytyy, tarkistetaan, onko salasana oikein
        password_correct = pl.verify(req_body['password'], user[2])
        if not password_correct:
            raise Exception('user not found2')

        #3. jos salasana on oikein, luodaan access_token jwt
        sub = str(uuid.uuid4())

        cursor = cnx.cursor()
        cursor.execute('UPDATE users SET access_jti = (%s) WHERE username = (%s)', (sub, req_body['username']))
        cnx.commit()

        # encode luo payloadista (dictionary) access_token_jwtn
        access_token = jwt.encode({'sub': sub, 'iat': datetime.datetime.now(datetime.UTC),
                                   'nbf': datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=10)}, SECRET)

        return access_token
    except Exception as e:
        cnx.rollback()


def register(cnx, reg_body):
    try:
        cursor = cnx.cursor()
        cursor.execute('INSERT INTO users(username, password, auth_role_id) VALUES(%s, %s, %s)',
                       (reg_body['username'], pl.hash(reg_body['password']), 1))
        cnx.commit()
        user = {'id': cursor.lastrowid, 'username': reg_body['username']}
        cursor.close()
        return user
    except Exception as e:
        cnx.rollback()
        raise e

def get_logged_in_user(cnx, sub):
    cursor = cnx.cursor()
    cursor.execute('SELECT id, username, auth_role_id FROM users WHERE access_jti = (%s)', (sub,))
    user = cursor.fetchone()
    if user is None:
        raise Exception('user not found')

    return {'id': user[0], 'username': user[1], 'role': user[2]}

def remove_user_by_id(cnx, user_id):
    cursor = None
    try:
        cursor = cnx.cursor()
        cursor.execute('DELETE FROM users WHERE id = (%s)', (user_id,))
        cnx.commit()
    except Exception as e:
        cnx.rollback()
        raise e
    finally:
        if cursor is not None:
            cursor.close()
