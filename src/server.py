import hashlib
from socket import *
import os
from Utilities import database_manager as database
from RequestHandlers import list as ListRequestHandler
from RequestHandlers import authentication as AuthRequestHandler
from RequestHandlers import upload as UploadRequestHandler
from RequestHandlers import download as DownloadRequestHandler
from RequestHandlers import exit as ExitRequestHandler
from Utilities import message_parser
from Utilities import message_serializer
from Utilities import constants
from Utilities import codes

# Server constants
BACKLOG = 16
PORT = 3000
CHECKSUM_CRLF_LENGTH = 66
MESSAGE_SIZE_CRLF_LENGTH = 18
DEFAULT_BUFFER = 1024


def send_error_response(connection_socket: socket, code: codes.Status):
    """
    Sends a response to the user with the specified code
    :param code: Status
    :param connection_socket: socket
    """
    response_string = message_serializer.build_response_string(code, file_size=0)
    response_string = cast_bytes(response_string)
    content = cast_bytes('')
    try:
        connection_socket.send(response_string)
        connection_socket.send(content)
    except ConnectionAbortedError as e:
        print('Disconnecting aborted socket')
        connection_socket.close()
    except OSError as e:
        print('Disconnecting aborted socket')
        connection_socket = None


def cast_bytes(content) -> bytes:
    """
    converts content to bytes
    :param content: str or bytes
    :return: the content as bytes
    """
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

    # print server details
    print("Server name:", gethostname())
    print("Server ip:", gethostbyname(gethostname()))
    print('Server port:', server_port)

    while True:
        # accept queued connection
        connection_socket, client_address = server_socket.accept()
        connected = True
        print('Connecting to:', client_address)

        # while a client is connected
        while connected:

            response_string = ''
            content = b''
            is_error = False

            # receive the message from the socket
            try:
                full_message, checksum, message_no_checksum = receive_message(connection_socket)
            except (ValueError, OSError) as e:
                # message not appropriately formatted
                print(client_address, 'Error in message retrieval', sep=':\t')
                send_error_response(connection_socket, codes.INTERNAL_SERVER_ERROR)
                connected = False
                is_error = True

            if not is_error and not is_correct_checksum(checksum, message_no_checksum):
                # message was changed during transmission
                print(client_address, 'Message received incorrectly', sep=':\t')
                send_error_response(connection_socket, codes.MESSAGE_CORRUPTED)
                is_error = True

            # parse message
            try:
                parsed_request = message_parser.parse_message(full_message)  # parse the message
            except:
                # message was incorrectly formatted
                print(client_address, 'Message formatted incorrectly', sep=':\t')
                send_error_response(connection_socket, codes.INVALID_FORMAT)
                is_error = True

            # public endpoint AUTH
            try:
                if not is_error and parsed_request[constants.PARAMETERS_KEY][constants.METHOD_KEY] == constants.AUTH:
                    print(client_address, parsed_request[constants.PARAMETERS_KEY][constants.METHOD_KEY], sep=':\t')
                    email = parsed_request[constants.PARAMETERS_KEY][constants.AUTH_EMAIL_KEY]
                    password = parsed_request[constants.PARAMETERS_KEY][constants.AUTH_PASSWORD_KEY]
                    response_string, content = AuthRequestHandler.response(email, password)
            except:
                # key probably doesn't exist
                # TODO: find exception name, and send appropriate response
                is_error = True
                pass

            # protected endpoints LIST, UPLOAD, DOWNLOAD
            # Access key check
            if not is_error:
                method = parsed_request[constants.PARAMETERS_KEY][constants.METHOD_KEY]
            if not is_error and method != constants.EXIT and method != constants.AUTH:
                if constants.ACCESS_KEY not in parsed_request[constants.HEADERS]:
                    # access key was not provided
                    print(client_address, 'Missing access key', sep=':\t')
                    send_error_response(connection_socket, codes.ACCESS_DENIED)
                    is_error = True
                elif constants.ACCESS_KEY in parsed_request[constants.HEADERS]:
                    access_key = parsed_request[constants.HEADERS][constants.ACCESS_KEY]
                    email = parsed_request[constants.HEADERS][constants.USER]
                    if AuthRequestHandler.generate_access_key_decoded(email) != access_key:
                        # incorrect access key
                        print(client_address, 'Incorrect access key', sep=':\t')
                        send_error_response(connection_socket, codes.ACCESS_DENIED)
                        is_error = True

            # List Request
            try:
                if not is_error and parsed_request[constants.PARAMETERS_KEY][constants.METHOD_KEY] == constants.LIST:
                    print(client_address, parsed_request[constants.PARAMETERS_KEY][constants.METHOD_KEY], sep=':\t')
                    email = parsed_request[constants.HEADERS][constants.USER]
                    access_key = None
                    if not is_error:
                        access_key = parsed_request[constants.HEADERS][constants.ACCESS_KEY]
                    response_string, content = ListRequestHandler.response(email, access_key)
                    if is_error:
                        content = b''
            except FileNotFoundError:
                # key probably doesn't exist
                # TODO: find exception name, and send appropriate response
                is_error = True
                pass

            # Upload Request
            try:
                if not is_error and (
                        parsed_request[constants.PARAMETERS_KEY][constants.METHOD_KEY] == constants.UPLOAD) and \
                        (parsed_request[constants.FILE_SIZE_KEY] > 0):

                    file = b''

                    while len(file) < parsed_request[constants.FILE_SIZE_KEY]:
                        file += connection_socket.recv(DEFAULT_BUFFER)

                    # email = parsed_request[constants.HEADERS][constants.USER]
                    # access_key = parsed_request[constants.HEADERS][constants.ACCESS_KEY]
                    response_string, content = UploadRequestHandler.response(full_message.decode(), file)
                    if is_error:
                        content = b''
            except RuntimeError as e:
                print(client_address, 'User does not exist', sep=':\t')
                send_error_response(connection_socket, codes.USER_NOT_EXIST)
                is_error = True
            except Exception as e:
                raise e
                # key probably doesn't exist
                # TODO: find exception name, and send appropriate response
                pass

            # Download Request
            try:
                if not is_error and parsed_request[constants.PARAMETERS_KEY][
                    constants.METHOD_KEY] == constants.DOWNLOAD:
                    print(client_address, parsed_request[constants.PARAMETERS_KEY][constants.METHOD_KEY], sep=':\t')
                    email = parsed_request[constants.HEADERS][constants.USER]
                    file_name = parsed_request[constants.PARAMETERS_KEY]['file_name']
                    response_string, content = DownloadRequestHandler.response(email, file_name)
                    if is_error:
                        content = b''
            except Exception as e:
                raise e
                # key probably doesn't exist
                # TODO: find exception name, and send appropriate response
                pass

            # Exit Request
            try:
                if not is_error and \
                        parsed_request[constants.PARAMETERS_KEY][
                            constants.METHOD_KEY] == constants.EXIT and not is_error:
                    response_string, content = ExitRequestHandler.response()
                    print('Disconnecting from:', client_address)
                    response_string = cast_bytes(response_string)
                    content = cast_bytes(content)
                    connection_socket.send(response_string)
                    connection_socket.send(content)
                    connection_socket.close()
                    connected = False
                    continue
            except:
                # key probably doesn't exist
                # TODO: find exception name, and send appropriate response
                pass

            # send response
            if not is_error:
                response_string = cast_bytes(response_string)
                content = cast_bytes(content)
                connection_socket.send(response_string)
                connection_socket.send(content)


def receive_message(connection_socket):
    """
    Reads bytes from socket
    :param connection_socket:
    :return: bytes containing the full message received from the socket
    """
    checksum = connection_socket.recv(CHECKSUM_CRLF_LENGTH)  # checksum + CRLF
    message_size = connection_socket.recv(MESSAGE_SIZE_CRLF_LENGTH)  # message size + CRLF
    message = connection_socket.recv(int(message_size.decode()))  # receive the rest of the message

    return checksum + message_size + message, checksum.decode()[
                                              :-2].encode(), message_size + message  # message that was sent


# TODO: Change to generate checksums based on message + content
def is_correct_checksum(checksum: bytes, message_no_checksum: bytes) -> bool:
    """
    compares the checksum provided to the server generated checksum
    :param checksum:
    :param message_no_checksum:
    :return: true if checksums are the same
    """
    decoded_checksum = checksum.decode()
    generated_checksum = hashlib.sha256(message_no_checksum).hexdigest()
    return decoded_checksum == generated_checksum


if __name__ == '__main__':
    try:
        database.connect()
        launch()
        database.disconnect()
    except KeyboardInterrupt:
        database.disconnect()
        print('Server shutting down.')
