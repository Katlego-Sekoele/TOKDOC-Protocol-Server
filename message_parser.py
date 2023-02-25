import datetime
import hashlib
import sys
import os
from dotenv import load_dotenv

CHECKSUM_LENGTH = 64
CRLF_LENGTH = 2
MESSAGE_SIZE_LENGTH = 16
START = '{START}'
END = '{END}'
CRLF = '\r\n'
SPACE = ' '
START_METHOD = '{{START METHOD}}'
END_METHOD = '{{END METHOD}}'
START_HEADERS = '{{START HEADERS}}'
END_HEADERS = '{{END HEADERS}}'
START_FILE = '{{START FILE}}'
END_FILE = '{{END FILE}}'

DATA = 'DATA'
UPLOAD = 'UPLOAD'
AUTH = 'AUTH'

USER = 'USER'
ACCESS_KEY = 'ACCESS_KEY'
TIMESTAMP = 'TIMESTAMP'
AUTHORIZED = 'AUTHORIZED'

FILE_SIZE = 'FILE_SIZE'

PARAMETERS = 'parameters'
HEADERS = 'headers'
FILE_SIZE_KEY = 'file_size'


def parse_message(message):
    """
    Function that takes a message byte encoded and returns
    a dictionary of message elements as described in the TOKDOC protocol.
    """
    message = test_message()

    parsed = {}

    method_group_type = get_method_group_type(message)
    if method_group_type == AUTH:
        parsed[PARAMETERS] = get_auth_parameters(message)
    elif method_group_type == DATA:
        parsed[PARAMETERS] = get_data_parameters(message)
        parsed[HEADERS] = get_headers(message)
        parsed[FILE_SIZE_KEY] = get_file_size(message)
    else:
        raise TypeError('The method group type "'+method_group_type+'" is not supported')

    print(parsed)


# START TESTING STUFF
def encoded_auth_test():
    return str.encode(
        "5a32034ef2da2b10585068273adef5fd602b631b62b8527bb73d7669f2490aae\r\n77              \r\n{START}\r\n\r\n{{START METHOD}}\r\nAUTH test@test.com test\r\n{{END METHOD}}\r\n\r\n{{END}}"
    )


def encoded_data_test():
    return str.encode(
        "d59075b5224106ca9b6f9a83ded0cefe4be51f9c1fd5e45f3d76128e60de3a68\r\n314             \r\n{START}\r\n\r\n{{START METHOD}}\r\nDATA DOWNLOAD 127.0.0.1:3000 image.jpg\r\n{{END METHOD}}\r\n\r\n{{START HEADERS}}\r\nUSER:john@doe.com\r\nACCESS_KEY:kewuahcopfmw983c2[093mru0cum239rcum2[3pa[29cu,r\r\nTIMESTAMP:2023-02-22T20:14:31Z\r\n{{END HEADERS}}\r\n\r\n{{START FILE}}\r\nFILE_SIZE:33\r\njryghfiweufhjwemflnwefkwe\r\n{{END FILE}}\r\n\r\n{END}"
    )


def test_message():
    file_size = os.path.getsize('test_data/test.png')

    message = (START +
               CRLF + CRLF +
               START_METHOD +
               CRLF +
               DATA + SPACE + UPLOAD + SPACE + '127.0.0.1:3000' + SPACE + 'tested.png' +
               CRLF +
               END_METHOD +
               CRLF + CRLF +
               START_HEADERS +
               CRLF +
               USER + ':test@test.com' +
               CRLF +
               ACCESS_KEY + ':' + generate_access_key_decoded('test@test.com') +
               CRLF +
               TIMESTAMP + ':' + str(datetime.datetime.utcnow().isoformat()) +
               CRLF +
               END_HEADERS +
               CRLF + CRLF +
               START_FILE +
               CRLF +
               FILE_SIZE + ":" + str(file_size) +
               CRLF +
                END_FILE +
                CRLF + CRLF +
               END)

    message_length = len(message)

    message_length = str(message_length) + (16-len(str(message_length)))*" "

    message = message_length + CRLF + message

    hashed = hashlib.sha256(message.encode()).hexdigest()

    message = hashed + CRLF + message

    return message


def test_file():
    file = open('test_data/test.png', 'rb')
    file_bytes = file.read()
    file.close()

    return file_bytes

# END TESTING STUFF


def get_checksum(message):
    return message[:CHECKSUM_LENGTH]


def get_message_size(message):
    return int(message[CHECKSUM_LENGTH + CRLF_LENGTH:CHECKSUM_LENGTH + CRLF_LENGTH + MESSAGE_SIZE_LENGTH].strip())


def get_message_content(message):
    size = get_message_size(message)
    offset = CHECKSUM_LENGTH + CRLF_LENGTH + MESSAGE_SIZE_LENGTH + CRLF_LENGTH
    return message[offset: offset + CRLF_LENGTH + size]


def get_method_content(message):
    message_content = get_message_content(message)
    start_index = str(message_content).index(START_METHOD) + len(START_METHOD)
    end_index = str(message_content).index(END_METHOD)
    return message_content[start_index: end_index].strip('\r\n')


def get_auth_parameters(message):
    method_content = get_method_content(message)
    content_list = str(method_content).split()
    return {
        'method': content_list[0],
        'email': content_list[1],
        'password': content_list[2]
    }


def generate_access_key_decoded(email):
    load_dotenv()
    server_key = os.getenv('SERVER_KEY')
    pre_hash = server_key + email
    return hashlib.sha256(pre_hash.encode()).hexdigest()


def get_data_parameters(message):
    method_content = get_method_content(message)
    content_list = str(method_content).split()

    parameters = {
        'method_group': content_list[0],
        'method': content_list[1],
        'ip': content_list[2].split(':')[0],
        'port': content_list[2].split(':')[1],
    }

    try:
        parameters['file_name'] = content_list[3]
    except IndexError:
        pass

    return parameters


def get_method_group_type(message):
    return get_method_content(message).split()[0]


def get_method_type(message):
    return get_method_content(message).split()[1]


def get_header_content(message):
    message_content = get_message_content(message)
    start_index = str(message_content).index(START_HEADERS) + len(START_HEADERS)
    end_index = str(message_content).index(END_HEADERS)
    return message_content[start_index: end_index].strip('\r\n')


def get_headers(message):
    header_content = get_header_content(message)
    headers_list = header_content.split()
    headers = {}
    for header in headers_list:
        key = header[:header.index(':')]
        value = header[header.index(':') + 1:]
        headers[key] = value

    return headers


def get_file_size(message):
    message_content = get_message_content(message)
    start_index = str(message_content).index(START_FILE) + len(START_FILE)
    end_index = str(message_content).index(END_FILE)
    message_content = message_content[start_index: end_index].strip('\r\n')
    return int(message_content.split(':')[1])


def save_file_to_server(message, file_bytes):

    file_name = get_data_parameters(message)['file_name']
    file = open(file_name, 'wb')
    file.write(file_bytes)
    file.close()


parse_message(None)
