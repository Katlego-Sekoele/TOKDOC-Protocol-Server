"""
File containing functions to build a response message
"""
from Utilities.codes import *
from Utilities.checksum_utility import generate_checksum
from Utilities.constants import *


def build_response_string(status: Status, access_key=None, file_size: int = None, content: bytes = None) -> str:
    """
    :param file_size:
    :param status: codes.Status object
    :param access_key:
    :return: str -> string formatted response message according to TOKDOC protocol
    """
    message = (
            START +
            CRLF + CRLF +
            START_RESPONSE +
            CRLF +
            str(status.code) + SPACE + QUOTES + status.status + QUOTES
    )

    if access_key:
        message += SPACE + access_key

    if file_size is not None:
        message += SPACE + str(file_size)

    message += (
            CRLF +
            END_RESPONSE +
            CRLF + CRLF +
            END
    )

    message_size = len(message.encode())
    message = (str(message_size) + (MESSAGE_SIZE_LENGTH - len(str(message_size))) * " " +
               CRLF + message)

    checksum = generate_checksum(message, content=content)
    return checksum + CRLF + message
