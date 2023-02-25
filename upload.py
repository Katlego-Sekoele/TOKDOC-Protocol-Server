# handle upload request
from datetime import *
import database_manager as database


def save_in_db(type, filename, id):
    command = 'INSERT INTO users (type, filepath, upload_date, owner ID) VALUES (%s, %s)'
    cred = (type, filename, datetime.now, id)
    database.query(command, cred)


def save_file(filename, filebytes):
    file = open(filename, 'wb')
    file.write(filebytes)
    file.close()
