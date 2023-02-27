import hashlib

import constants
from message_parser import get_message_string


def get_checksum(message):
    """
    :param message:
    :return: str -> the checksum provided in the message
    """
    message = get_message_string(message)
    return message[:constants.CHECKSUM_LENGTH]


def generate_checksum(message):
    message = get_message_string(message)
    return hashlib.sha256(message.encode()).hexdigest()
