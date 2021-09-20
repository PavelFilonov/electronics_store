import mysql.connector
from mysql.connector import Error

configs = dict(host='localhost',
               database='shop',
               user='root',
               password='')


def get_db():
    connection = mysql.connector.connect(**configs)
    cursor = connection.cursor()
    return connection, cursor


def close_db(connection, cursor):
    cursor.close()
    connection.close()
