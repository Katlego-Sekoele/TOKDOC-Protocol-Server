import hashlib
from socket import *
import os
from Utilities import database_manager as database
from RequestHandlers import list as ListRequestHandler
from RequestHandlers import authentication as AuthRequestHandler
from RequestHandlers import upload as UploadRequestHandler
from RequestHandlers import download as DownloadRequestHandler
from Utilities import message_parser
from Utilities import message_serializer
from Utilities import constants
from Utilities import codes

BACKLOG = 4
PORT = 3000
CHECKSUM_CRLF_LENGTH = 66
MESSAGE_SIZE_CRLF_LENGTH = 18
DEFAULT_BUFFER = 1024


def cast_bytes(content) -> bytes:
    if isinstance(content, str):
        return content.encode()
    elif isinstance(content, bytes):
        return content
    else:
        raise TypeError('The content must be bytes or string. Received', type(content))


def launch():
    """
    Function that will start up the server. Will start listening
    for connection requests and handle incoming and outgoing messages.
    :return:
    """
    # listen to a TCP socket
    server_port = int(os.getenv('PORT')) | PORT
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', server_port))
    server_socket.listen(BACKLOG)

    while True:
        connection_socket, client_address = server_socket.accept()

        full_message, checksum, message_no_checksum = receive_message(connection_socket)

        response_string = ''
        content = b''

        if not is_correct_checksum(checksum, message_no_checksum):
            # message was changed during transmission
            response_string = message_serializer.build_response_string(codes.MESSAGE_CORRUPTED, file_size=0)
            response_string = cast_bytes(response_string)
            content = cast_bytes(content)
            connection_socket.send(response_string)
            connection_socket.send(content)
            connection_socket.close()
            continue

        try:
            parsed_request = message_parser.parse_message(full_message)  # parse the message
        except:
            # message was incorrectly formatted
            response_string = message_serializer.build_response_string(codes.INVALID_FORMAT, file_size=0)
            response_string = cast_bytes(response_string)
            content = cast_bytes(content)
            connection_socket.send(response_string)
            connection_socket.send(content)
            connection_socket.close()
            continue

        try:
            if parsed_request[constants.PARAMETERS_KEY][constants.METHOD_KEY] == constants.AUTH:
                email = parsed_request[constants.PARAMETERS_KEY][constants.AUTH_EMAIL_KEY]
                password = parsed_request[constants.PARAMETERS_KEY][constants.AUTH_PASSWORD_KEY]
                response_string, content = AuthRequestHandler.response(email, password)
        except:
            # key probably doesn't exist
            # TODO: find exception name, and send appropriate response
            pass

        try:
            if parsed_request[constants.PARAMETERS_KEY][constants.METHOD_KEY] == constants.LIST:
                email = parsed_request[constants.HEADERS][constants.USER]
                access_key = parsed_request[constants.HEADERS][constants.ACCESS_KEY]
                response_string, content = ListRequestHandler.response(email, access_key)
        except FileNotFoundError:
            # key probably doesn't exist
            # TODO: find exception name, and send appropriate response
            pass

        try:
            if (parsed_request[constants.PARAMETERS_KEY][constants.METHOD_KEY] == constants.UPLOAD) and \
                    (parsed_request[constants.FILE_SIZE_KEY] > 0):

                file = b''

                while len(file) < parsed_request[constants.FILE_SIZE_KEY]:
                    file += connection_socket.recv(DEFAULT_BUFFER)

                # email = parsed_request[constants.HEADERS][constants.USER]
                # access_key = parsed_request[constants.HEADERS][constants.ACCESS_KEY]
                response_string, content = UploadRequestHandler.response(full_message.decode(), file)
        except:
            # key probably doesn't exist
            # TODO: find exception name, and send appropriate response
            pass

        try:
            if parsed_request[constants.PARAMETERS_KEY][constants.METHOD_KEY] == constants.DOWNLOAD:

                email = parsed_request[constants.HEADERS][constants.USER]
                access_key = parsed_request[constants.HEADERS][constants.ACCESS_KEY]
                file_name = parsed_request[constants.PARAMETERS_KEY]['filename']
                response_string, content = DownloadRequestHandler.response(email, file_name)
        except:
            # key probably doesn't exist
            # TODO: find exception name, and send appropriate response
            pass

        # send response_string and content

        response_string = cast_bytes(response_string)
        content = cast_bytes(content)
        connection_socket.send(response_string)
        connection_socket.send(content)
        connection_socket.close()


def receive_message(connection_socket):
    checksum = connection_socket.recv(CHECKSUM_CRLF_LENGTH)  # checksum + CRLF
    message_size = connection_socket.recv(MESSAGE_SIZE_CRLF_LENGTH)  # message size + CRLF
    message = connection_socket.recv(int(message_size.decode()))  # receive the rest of the message

    return checksum + message_size + message, checksum.decode()[
                                              :-2].encode(), message_size + message  # message that was sent


def is_correct_checksum(checksum: bytes, message_no_checksum: bytes) -> bool:
    decoded_checksum = checksum.decode()
    generated_checksum = hashlib.sha256(message_no_checksum).hexdigest()
    return decoded_checksum == generated_checksum


if __name__ == '__main__':
    database.connect()
    launch()
    database.disconnect()
