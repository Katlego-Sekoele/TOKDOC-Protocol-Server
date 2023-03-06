import hashlib
import Utilities.constants as constants
from Utilities.message_parser import get_message_string as get_message_string


def get_checksum(message) -> str:
    """
    :param message:
    :return: str -> the checksum provided in the message
    """
    message = get_message_string(message)
    return message[:constants.CHECKSUM_LENGTH]


def generate_checksum(message) -> str:
    """
    :param message:
    :return: str -> a sha256 checksum of the given message
    """
    message = get_message_string(message)
    return hashlib.sha256(message.encode()).hexdigest()
