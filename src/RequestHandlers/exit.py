# authenticating user logging in details and signing up users
# making use of Database and dictionaries
import hashlib
import os

from dotenv import load_dotenv

from Utilities import codes, message_serializer
from Utilities import database_manager as database


def response() -> tuple:

    response_string = message_serializer.build_response_string(codes.SUCCESS, file_size=0)
    return response_string, ''
