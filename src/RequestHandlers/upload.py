# receiving a file from client
from datetime import *
from src.Utilities import database_manager as database
from src.Utilities import message_parser as m_breaker
import os


def save_filename_to_db(filename, ID):
    filename, type = os.path.splitext(filename)
    command = 'INSERT INTO users (type, filepath, upload_date, owner ID) VALUES (%s, %s)'
    cred = (type, filename, datetime.now, ID)
    database.query(command, cred)
    save_file_to_server(filename)


def save_file(message, file_bytes) -> bytes:
    """
    saves the file to the server
    :param message:
    :param file_bytes: the bytes of the file to save
    """
    message = m_breaker.get_message_string(message)
    file_name = m_breaker.get_data_parameters(message)['file_name']
    id = m_breaker.get_headers(message)['USER']
    file = open(file_name, 'wb')
    file.write(file_bytes)
    file.close()
    save_filename_to_db(file_name, id)
