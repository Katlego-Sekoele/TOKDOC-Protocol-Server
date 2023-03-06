# receiving a file from client
from datetime import *

from Utilities import message_serializer
from Utilities import database_manager as database
from Utilities import message_parser as m_breaker
from Utilities import constants
from Utilities import codes
import os


def response(message: str, file: bytes, access_key=None) -> tuple:
    files_string = ''

    save_file(message, file)

    code = codes.SUCCESS

    response_string = message_serializer.build_response_string(code, file_size=0)
    return response_string, files_string.strip('\r\n')


def save_file(message, file_bytes):
    """
    saves the file to the server and calls to save the file to the database
    :param message:
    :param file_bytes: the bytes of the file to save
    """
    message = m_breaker.get_message_string(message)
    file_name = m_breaker.get_data_parameters(message)['file_name']
    email = m_breaker.get_headers(message)[constants.USER]

    try:
        authorized = m_breaker.get_headers(message)[constants.AUTHORIZED]
    except KeyError as e:
        authorized = None
    except Exception as e:
        # most likely occured because there is no AUTHORIZED key in the headers
        # TODO: find the exact exception
        raise e

    file = open(file_name, 'wb')
    file.write(file_bytes)
    file.close()
    save_filename_to_db(file_name, email, authorized)


def save_filename_to_db(filename, owner_email, authorized=None):
    throwaway, file_type = os.path.splitext(filename)

    user_id = get_user_id(owner_email)

    command = 'INSERT INTO Resources (type, resource_path, upload_date, user_id, public) VALUES (%s, %s, %s, %s, %s)'
    cred = (file_type, filename, datetime.now(), user_id, authorized is None)
    result = database.query(command, cred)
    database.commit()


    if authorized:
        file_command = 'SELECT * FROM Resources WHERE resource_path = %s'
        file_params = (filename,)
        file_id = database.query(file_command, file_params)[0]['resource_id']

        for email in authorized:
            access_user_id = get_user_id(email)
            access_query = 'INSERT INTO Access (user_id, file_id) VALUES (%s, %s)'
            access_params = (access_user_id, file_id)
            access_result = database.query(access_query, access_params)
            database.commit()


def get_user_id(email: str):
    query = "SELECT * FROM Users WHERE email = %s"
    params = (email,)
    result = database.query(query, params)

    if len(result) > 0:
        return result[0]['user_id']
    else:
        raise RuntimeError('User with the specified email,', email, ', not found.')

