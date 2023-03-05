"""
File containing functions to handle the parsing of a TOKDOC formatted message.
"""
import datetime
import hashlib
import os
import platform

from dotenv import load_dotenv
from Utilities import constants


def parse_message(message) -> dict:
    """
    Function that takes a string message and returns
    a dictionary of message elements as described in the TOKDOC protocol.

    The message must be in one of the following forms:
    <checksum>\r\n<message_size>\r\n{START}\r\n\r\n{{START METHOD}}\r\nAUTH <email> <password>\r\n{{END METHOD}}\r\n\r\n{{END}}
    <checksum>\r\n<message_size>\r\n{START}\r\n\r\n{{START METHOD}}\r\nEXIT <email> <password>\r\n{{END METHOD}}\r\n\r\n{{END}}
    <checksum>\r\n<message_size>\r\n{START}\r\n\r\n{{START METHOD}}\r\nDATA <method> <ip>:<port> [<file_name>]\r\n{{END METHOD}}\r\n\r\n{{START HEADERS}}\r\nUSER:<email>\r\nACCESS_KEY:<access_key>\r\n[TIMESTAMP:<iso format datetime>]\r\n[AUTHORIZED:(<email>,<email>,...)]\r\n{{END HEADERS}}\r\n\r\n{{START FILE}}\r\nFILE_SIZE:<size>\r\n{{END FILE}}\r\n\r\n{{END}}

    [] -> optional
    <> -> replace with appropriate data
    ... -> 0 to many
    ? -> may not exist

    :return: message dictionary -> a dictionary containing some or all of the following:
    {
        'parameters' : {
            'method_group' -> string?,
            'method' -> string,
            'ip' -> string?,
            'port' -> int?,
            'filename' -> string?,
            'email' -> string?,
            'password' -> string?
        },
        'headers' ?: {
            'USER' -> string,
            'ACCESS_KEY' -> string,
            'TIMESTAMP' -> string?,
            'AUTHORIZED' -> string[]?,
        },
        'file_size' -> int?
    }

    e.g.
    {
        'parameters': {
            'method_group': 'DATA',
            'method': 'UPLOAD',
            'ip': '127.0.0.1',
            'port': 3000,
            'file_name': 'tested.png'
        },
        'headers': {
            'USER': 'test@test.com',
            'ACCESS_KEY': '081c07e1074a3fc784799e5f78799fe276a7aed7d2656b6a4b7028f3dc39775a',
            'TIMESTAMP': '2023-02-26T23:14:23.562854',
            'AUTHORIZED': ['test@test.com', 'test2@test2.com']
        },
        'file_size': 239937
    }

    e.g.
    {
        'parameters': {
            'method': 'AUTH',
            'email': 'test@test.com',
            'password': 'test'
        }
    }
    """

    message = get_message_string(message)

    parsed = {}

    method_group_type = get_method_group_type(message)
    if method_group_type == constants.AUTH or method_group_type == constants.EXIT:
        parsed[constants.PARAMETERS_KEY] = get_auth_exit_parameters(message)
    elif method_group_type == constants.DATA:
        parsed[constants.PARAMETERS_KEY] = get_data_parameters(message)
        parsed[constants.HEADERS] = get_headers(message)
        parsed[constants.FILE_SIZE_KEY] = get_file_size(message)
    else:
        raise TypeError('The method group type "' + method_group_type + '" is not supported')

    return parsed


# START TESTING STUFF
def encoded_auth_test() -> bytes:
    """
    :return: bytes -> an encoded AUTH message
    """
    return str.encode(
        "5a32034ef2da2b10585068273adef5fd602b631b62b8527bb73d7669f2490aae\r\n77              \r\n{START}\r\n\r\n{{"
        "START METHOD}}\r\nAUTH test@test.com test\r\n{{END METHOD}}\r\n\r\n{{END}} "
    )


def encoded_data_test() -> bytes:
    """
    :return: bytes -> an encoded DATA message
    """
    return str.encode(
        "d59075b5224106ca9b6f9a83ded0cefe4be51f9c1fd5e45f3d76128e60de3a68\r\n314             \r\n{START}\r\n\r\n{{"
        "START METHOD}}\r\nDATA DOWNLOAD 127.0.0.1:3000 image.jpg\r\n{{END METHOD}}\r\n\r\n{{START "
        "HEADERS}}\r\nUSER:john@doe.com\r\nACCESS_KEY:kewuahcopfmw983c2[093mru0cum239rcum2[3pa[29cu,"
        "r\r\nTIMESTAMP:2023-02-22T20:14:31Z\r\n{{END HEADERS}}\r\n\r\n{{START "
        "FILE}}\r\nFILE_SIZE:33\r\njryghfiweufhjwemflnwefkwe\r\n{{END FILE}}\r\n\r\n{END} "
    )


def test_message() -> str:
    """
    :return: str -> a DATA message
    """
    if platform.system() == 'Windows':
        file_size = os.stat(".\\test_data\\test.png").st_size
    else:
        file_size = os.stat('./test_data/test.png').st_size

    message = (constants.START +
               constants.CRLF + constants.CRLF +
               constants.START_METHOD +
               constants.CRLF +
               constants.DATA + constants.SPACE + constants.UPLOAD + constants.SPACE + '127.0.0.1:3000' + constants.SPACE + 'tested.png' +
               constants.CRLF +
               constants.END_METHOD +
               constants.CRLF + constants.CRLF +
               constants.START_HEADERS +
               constants.CRLF +
               constants.USER + ':test@test.com' +
               constants.CRLF +
               constants.ACCESS_KEY + ':' + generate_access_key_decoded('test@test.com') +
               constants.CRLF +
               constants.TIMESTAMP + ':' + str(datetime.datetime.utcnow().isoformat()) +
               constants.CRLF +
               constants.AUTHORIZED + ':' + '(test@test.com,test2@test2.com)' +
               constants.CRLF +
               constants.END_HEADERS +
               constants.CRLF + constants.CRLF +
               constants.START_FILE +
               constants.CRLF +
               constants.FILE_SIZE + ":" + str(file_size) +
               constants.CRLF +
               constants.END_FILE +
               constants.CRLF + constants.CRLF +
               constants.END)

    message_length = len(message)

    message_length = str(message_length) + (16 - len(str(message_length))) * " "

    message = message_length + constants.CRLF + message

    hashed = hashlib.sha256(message.encode()).hexdigest()

    message = hashed + constants.CRLF + message

    return message


def test_file() -> bytes:
    """
    :return: bytes -> the bytes of a test file
    """
    file = open('../test_data/test.png', 'rb')
    file_bytes = file.read()
    file.close()

    return file_bytes


# END TESTING STUFF


def get_message_size(message) -> int:
    """
    :param message:
    :return: int -> message size as provided in the message
    """
    message = get_message_string(message)
    return int(message[
               constants.CHECKSUM_LENGTH + constants.CRLF_LENGTH:constants.CHECKSUM_LENGTH + constants.CRLF_LENGTH + constants.MESSAGE_SIZE_LENGTH].strip())


def get_message_content(message) -> str:
    """
    :param message:
    :return: str -> the message content excluding the checksum and message size
    """
    message = get_message_string(message)
    size = get_message_size(message)
    offset = constants.CHECKSUM_LENGTH + constants.CRLF_LENGTH + constants.MESSAGE_SIZE_LENGTH + constants.CRLF_LENGTH
    return message[offset: offset + constants.CRLF_LENGTH + size]


def get_method_content(message) -> str:
    """
    :param message:
    :return: str -> The content enclosed with in the {{START METHOD}}, {{END METHOD}} tags
    """
    message = get_message_string(message)
    message_content = get_message_content(message)
    start_index = str(message_content).index(constants.START_METHOD) + len(constants.START_METHOD)
    end_index = str(message_content).index(constants.END_METHOD)
    return message_content[start_index: end_index].strip('\r\n')


def get_auth_exit_parameters(message) -> dict:
    """
    :param message:
    :return: dict -> returns a dictionary
    {
        'method': 'AUTH',
        'email': str,
        'password': str
    }
    """
    if get_method_group_type(message) != constants.AUTH and get_method_group_type(message) != constants.EXIT:
        raise TypeError('The method group type must be "AUTH" or "EXIT" to use this function')

    message = get_message_string(message)
    method_content = get_method_content(message)

    content_list = str(method_content).split()

    if content_list[0] == constants.EXIT:
        # exit request
        return {
            'method': content_list[0]
        }

    return {
        'method': content_list[0],
        'email': content_list[1],
        'password': content_list[2]
    }


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


def get_data_parameters(message) -> dict:
    """
    :param message:
    :return: dict -> {
        'method_group': str,
        'method': str,
        'ip': str,
        'port': int,
    }
    """
    message = get_message_string(message)
    method_content = get_method_content(message)
    content_list = str(method_content).split()

    parameters = {
        'method_group': content_list[0],
        'method': content_list[1],
        'ip': content_list[2].split(':')[0],
        'port': int(content_list[2].split(':')[1]),
    }

    try:
        parameters['file_name'] = content_list[3]
    except IndexError:
        pass

    return parameters


def get_method_group_type(message) -> str:
    """
    Returns the type of message (AUTH or DATA)
    :param message:
    :return: str
    """
    message = get_message_string(message)
    return get_method_content(message).split()[0]


def get_method_type(message) -> str:
    """
    Returns the method type (DOWNLOAD, UPLOAD, or LIST)
    :param message:
    :return:
    """
    message = get_message_string(message)
    return get_method_content(message).split()[1]


def get_header_content(message) -> str:
    """
    :param message:
    :return: str -> the string contained in the {{START HEADERS}}, {{END HEADERS}} tags
    """
    message_content = get_message_content(message)
    start_index = str(message_content).index(constants.START_HEADERS) + len(constants.START_HEADERS)
    end_index = str(message_content).index(constants.END_HEADERS)
    return message_content[start_index: end_index].strip('\r\n')


def get_headers(message) -> dict:
    """
    :param message:
    :return: dict -> containing key value pairs of all the headers
    """
    message = get_message_string(message)
    header_content = get_header_content(message)
    headers_list = header_content.split()
    headers = {}
    for header in headers_list:
        key = header[:header.index(':')]
        if key == constants.AUTHORIZED:
            value = header[header.index(':') + 2: -1]
            value = value.replace(' ', '')
            value = value.split(',')
        else:
            value = header[header.index(':') + 1:]

        if value:
            headers[key] = value

    return headers


def get_file_size(message) -> int:
    """
    :param message:
    :return: int -> file size as specified in the message
    """
    message = get_message_string(message)
    message_content = get_message_content(message)
    start_index = str(message_content).index(constants.START_FILE) + len(constants.START_FILE)
    end_index = str(message_content).index(constants.END_FILE)
    message_content = message_content[start_index: end_index].strip('\r\n')
    return int(message_content.split(':')[1])

def get_message_string(message) -> str:
    """
    :param message: string or bytes of the message
    :return: the string formatted message
    """
    if isinstance(message, bytes):
        return bytes(message).decode()
    elif isinstance(message, str):
        return message
    else:
        raise TypeError('The message must either be of type bytes or string. You message was type', type(message))
