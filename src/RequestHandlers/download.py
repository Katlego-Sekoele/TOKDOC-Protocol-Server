# sending a file to the client
import os
from socket import *

from Utilities import database_manager as database
from Utilities import message_serializer as m_builder
from Utilities import message_parser as m_breaker
from Utilities import codes


def response(email, filename):

    response_string = ''
    file_bytes = b''
    code = codes.SUCCESS

    if not valid_filename(filename):
        code = codes.FILE_NOT_FOUND
    else:
        if not is_public(filename) or not has_access():
            code = codes.ACCESS_DENIED
        else:
            file_bytes, file_size = send()

    response_string = m_builder.build_response_string(code, file_size=file_size)
    return response_string, file_bytes



# checks if file name entered is valid
def valid_filename(filename):
    valid = False
    query = "SELECT resource_path FROM resources WHERE resource_path = %s"
    results = database.query(query, filename)

    file_exists = results

    if file_exists is not None and len(file_exists) > 0:
        valid = True

    return valid


# this method works when valid_filename is true
def is_public(filename):
    public = False
    query = "SELECT public FROM Recourses WHERE resource_path = %s"
    access = database.query(query, filename)

    if access == 1:
        public = True

    return public


# checks if an access ID exists for the client
def has_access(filename, email):
    access = False
    query = "SELECT resource_id FROM resources where resource_path = %s"

    resource_id = database.query(query, filename)[0]

    query = "SELECT user_id FROM resources where email = %s"
    user_id = database.query(query, email)[0]

    query = "SELECT access_id FROM Access where user_id=%s AND resource_id=%s"
    info = (user_id, resource_id)

    key = database.query(query, info)

    if key is not None:
        access = True

    return access


# uploading the actual contents of the file to the client :)
def send(filename):

    file = open(filename, "rb")
    file_size = os.path.getsize(filename)
    data = file.read()
    file.close()

    return data, file_size
