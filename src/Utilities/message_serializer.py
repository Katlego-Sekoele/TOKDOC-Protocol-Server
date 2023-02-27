from codes import *
from checksum_utility import generate_checksum
from constants import *


def build_auth_response_string(status_code: Status, access_key=None) -> str:
    message = (
            START +
            CRLF + CRLF +
            START_RESPONSE +
            CRLF +
            str(status_code.code) + SPACE + QUOTES + status_code.status + QUOTES
    )

    if access_key:
        message += SPACE + access_key

    message += (
        CRLF +
        END_RESPONSE +
        CRLF + CRLF +
        END
    )

    message_size = len(message.encode())
    message = (str(message_size) + (MESSAGE_SIZE_LENGTH-len(str(message_size)))*" " +
               CRLF + message)

    checksum = generate_checksum(message)
    return (checksum + CRLF + message)


print(build_auth_response_string(SUCCESSFUL_AUTHENTICATION))
