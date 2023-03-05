class Status:
    def __init__(self, code: int, status: str):
        self.code = code
        self.status = status

    def code(self):
        return self.code

    def status(self):
        return self.status


SUCCESS = Status(**{'code': 201, 'status': 'Success'})
SUCCESSFUL_AUTHENTICATION = Status(**{'code': 200, 'status': 'Successful authentication'})
INCORRECT_CREDENTIALS = Status(**{'code': 501, 'status': 'Incorrect credentials'})
MESSAGE_CORRUPTED = Status(**{'code': 502, 'status': 'Corrupted'})
SIGN_UP_ERROR = Status(**{'code': 503, 'status': 'Sign up error'})
FILE_NOT_FOUND = Status(**{'code': 301, 'status': 'File not found'})
NO_FILES_FOUND = Status(**{'code': 303, 'status': 'No files found'})
ACCESS_DENIED = Status(**{'code': 302, 'status': 'Access to this file is denied'})
INTERNAL_SERVER_ERROR = Status(**{'code': 500, 'status': 'Internal Server Error'})
EXITING_AUTHORIZED = Status(**{'code': 201, 'status': 'Exiting authorized'})
INVALID_FORMAT = Status(**{'code': 504, 'status': 'Invalid format'})
