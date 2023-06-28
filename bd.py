import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_db(user, password):
    connection = psycopg2.connect(user=user, password=password)
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    try:
        cursor.execute('create database bdata_vk;')
    except Exception as err:
        print(f'Could not create database {err}')
    finally:
        cursor.close()
        connection.close()
