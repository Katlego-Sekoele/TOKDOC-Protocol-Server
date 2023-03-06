"""
sending a file from client
functions to handle the downloading of a file
from the server to the client
"""
import os
from Utilities import codes
from Utilities import database_manager as database
from Utilities import message_serializer as m_builder


def response(email, filename):
    """
    generates a response message to send back to the client
    :param filename:
    :param email:
    :return: (response message, response data)
    """
    response_string = ''
    file_bytes = b''
    code = codes.SUCCESS
    file_size = 0

    if not valid_filename(filename):
        code = codes.FILE_NOT_FOUND
    elif not is_public(filename) and not has_access(filename, email):
        code = codes.ACCESS_DENIED
    else:
        file_bytes, file_size = send(filename)

    response_string = m_builder.build_response_string(code, file_size=file_size)
    return response_string, file_bytes


# checks if file name entered is valid
def valid_filename(filename):
    """
    Validate that the file exists in the database
    :param filename:
    :return:
    """
    valid = False
    query = "SELECT resource_path FROM resources WHERE resource_path = %s"
    results = database.query(query, (filename,))

    file_exists = results

    if file_exists is not None and len(file_exists) > 0:
        valid = True

    return valid


# this method works when valid_filename is true
def is_public(filename):
    """
    :param filename:
    :return: True if the file is public
    """
    public = False
    query = "SELECT public FROM Resources WHERE resource_path = %s"
    access = database.query(query, (filename,))

    public = access[0]['public'] == 1

    return public


# checks if an access ID exists for the client
def has_access(filename, email):
    """

    :param filename:
    :param email:
    :return: True if the user has access to this file
    """
    access = False
    query = "SELECT resource_id FROM Resources where resource_path = %s"

    resource_id = database.query(query, (filename,))[0]['resource_id']

    query = "SELECT user_id FROM Users where email = %s"
    user_id = database.query(query, (email,))[0]['user_id']

    query = "SELECT access_id FROM Access where user_id=%s AND file_id=%s"
    info = (int(user_id), int(resource_id))

    key = database.query(query, info)

    access = len(key) > 0

    return access


# uploading the actual contents of the file to the client :)
def send(filename):
    """
    :param filename:
    :return: (bytes of the file, file size)
    """
    file = open(filename, "rb")
    file_size = os.path.getsize(filename)
    data = file.read()
    file.close()

    return data, file_size
