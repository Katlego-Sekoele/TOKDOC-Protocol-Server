# logging user out
# making use of Database and dictionaries
import hashlib
import os

from dotenv import load_dotenv

from Utilities import codes, message_serializer
from Utilities import database_manager as database


def response() -> tuple:


    files_string = ''

    code = codes.SUCCESS

    response_string = message_serializer.build_response_string(code)
    return response_string, files_string.strip('\r\n')