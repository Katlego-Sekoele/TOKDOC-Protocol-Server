"""
Function to handle an exit request
"""
from Utilities import codes, message_serializer


def response() -> tuple:
    """
    generates a response message for the exit request
    :return:
    """
    response_string = message_serializer.build_response_string(codes.SUCCESS, file_size=0)
    return response_string, ''
