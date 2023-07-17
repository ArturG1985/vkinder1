import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def init_db(user, password):
    # Устанавливаем соединение с postgres
    connection = psycopg2.connect(user=user, password=password)
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    # Создаем курсор для выполнения операций с базой данных
    cursor = connection.cursor()
    try:
        cursor.execute('create database bdata_vk;')
    except Exception as err:
        print(f'Could not create database {err}')
    finally:
        # Закрываем соединение
        cursor.close()
        connection.close()
