import os
from dotenv import load_dotenv
from mysql.connector import Error
import mysql.connector

connection = None


def connect():
    load_dotenv()

    global connection
    connection = mysql.connector.connect(
        host=os.getenv("HOST"),
        database=os.getenv("DATABASE"),
        user=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        ssl_ca=os.getenv("SSL_CERT")
    )

    try:
        if connection.is_connected():
            cursor = connection.cursor()
        cursor.execute("select @@version ")
        version = cursor.fetchone()
        if version:
            print('Running version: ', version)
        else:
            print('Not connected.')
    except Error as e:
        raise Exception("Error while connecting to MySQL", e)


def query(query_template, query_values=None):
    # get cursor
    cursor = connection.cursor()
    # execute query
    cursor.execute(query_template, query_values)
    # get rows
    result_rows = cursor.fetchall()
    # get field names
    field_names = [i[0] for i in cursor.description]

    # map field names to value in dictionary
    entry = dict()
    results = []
    for row in result_rows:
        entry = dict()
        i = 0
        for column_value in row:
            entry[field_names[i]] = column_value
            i += 1
        results.append(entry)

    return results


def disconnect():
    connection.close()
