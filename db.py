import contextlib

import mysql.connector


def connect_to_dbx():
        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='reseptit')
        return cnx

# funktio joka yieldaa on generaattori
@contextlib.contextmanager
def connect_to_db():
        print("######### connect to db")
        cnx = None
        try:
                cnx = mysql.connector.connect(user='root', password='', host='localhost', database='reseptit')
                print("######### yilding connection")
                yield cnx
        except mysql.connector.Error as e:
                print("Error connecting to db")
                yield None

        finally:
                # finally mennään aina, onnistuttiin tai epäonnistuttiin
                print("######### inside finally")
                if cnx is not None:
                        print("######### closing connection")
                        cnx.close()

