import hashlib
from socket import *
import os
from Utilities import database_manager as database
from RequestHandlers import list as ListRequestHandler
from Utilities import message_parser
from Utilities import constants

BACKLOG = 4
PORT = 3000
CHECKSUM_CRLF_LENGTH = 66
MESSAGE_SIZE_CRLF_LENGTH = 18
DEFAULT_BUFFER = 1024


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

        if not is_correct_checksum(checksum, message_no_checksum):
            # message was changed during transmission
            connection_socket.close()
            continue

        parsed_request = message_parser.parse_message(full_message)  # parse the message

        if (parsed_request[constants.FILE_SIZE_KEY] > 0) and \
                (parsed_request[constants.PARAMETERS_KEY][constants.METHOD_KEY] == constants.UPLOAD):

            file = b''

            while len(file) < parsed_request[constants.FILE_SIZE_KEY]:
                file += connection_socket.recv(DEFAULT_BUFFER)

            message_parser.save_file_to_server(full_message, file)

        connection_socket.close()


def receive_message(connection_socket):
    checksum = connection_socket.recv(CHECKSUM_CRLF_LENGTH)  # checksum + CRLF
    message_size = connection_socket.recv(MESSAGE_SIZE_CRLF_LENGTH)  # message size + CRLF
    message = connection_socket.recv(int(message_size.decode()))  # receive the rest of the message

    return checksum + message_size + message, checksum.decode()[:-2].encode(), message_size + message  # message that was sent


def is_correct_checksum(checksum: bytes, message_no_checksum: bytes) -> bool:
    decoded_checksum = checksum.decode()
    generated_checksum = hashlib.sha256(message_no_checksum).hexdigest()
    return decoded_checksum == generated_checksum


if __name__ == '__main__':
    database.connect()
    launch()
    database.disconnect()
