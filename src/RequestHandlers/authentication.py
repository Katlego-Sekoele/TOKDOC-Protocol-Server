"""
authenticating user logging in details and signing up users
"""
import hashlib
import os
from dotenv import load_dotenv
from Utilities import codes, message_serializer


def response(email: str, password: str, database=None) -> tuple:
    """
    generates a response message to send back to the client
    :param email:
    :param password:
    :return: (response message, response data)
    """
    authenticated = check_user(email, password, database=database)  # authenticate or register user result
    files_string = ''
    access_key = 'null'

    code = None
    if authenticated:
        code = codes.SUCCESS
        access_key = generate_access_key_decoded(email)
    else:
        code = codes.INCORRECT_CREDENTIALS

    response_string = message_serializer.build_response_string(code, access_key=access_key)
    return response_string, files_string.strip('\r\n')


# register new
def register_user(email, password, database=None):
    """
    Registers a user. i.e. adds user information to the database
    :param email:
    :param password:
    :return:
    """
    done = False

    # sql command
    command = "INSERT INTO Users (email, password) VALUES (%s, %s)"
    creds = (email, password)
    database.query(command, creds)
    database.commit()
    done = True

    return done


# check member
def check_user(email, password, database=None) -> bool:
    """
    :param email:
    :param password:
    :return: True if user exists
    """
    found = False

    #  check user_exists
    command_find_user = "SELECT email FROM Users WHERE email = %s"
    creds_find_user = (email,)
    result_find_user = database.query(command_find_user, creds_find_user)
    if len(result_find_user) > 0:
        # user found, check credentials
        # sql command
        command_check_credentials = "SELECT email FROM Users WHERE email = %s AND password = %s"
        creds_check_credentials = (email, password)
        result = database.query(command_check_credentials, creds_check_credentials)

        if result is not None and len(result) > 0:
            found = True
    else:
        # user not found, create user
        found = register_user(email, password, database=database)

    return found


def generate_access_key_decoded(email) -> str:
    """
    Generates an access key for the provided email
    :param email:
    :return: str -> access key
    """
    load_dotenv()
    server_key = os.getenv('SERVER_KEY')
    pre_hash = server_key + email
    return hashlib.sha256(pre_hash.encode()).hexdigest()
