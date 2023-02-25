# handle upload request
from datetime import *
import mysql.connector

db = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
)

cursor = db.cursor()

def save_in_db(type, filename, id):
    command = 'INSERT INTO users (type, filepath, upload_date, owner ID) VALUES (%s, %s)'
    cred = (type, filename, datetime.now, id)
    cursor.execute(command, cred)


def save_file(filename, filebytes):
    file = open(file_name, 'wb')
    file.write(filebytes)
    file.close

