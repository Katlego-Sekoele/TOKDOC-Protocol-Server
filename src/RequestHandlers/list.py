"""
listing all the available files
functions to handle the listing of accessible files
"""
from Utilities import codes
from Utilities import message_serializer as message_serializer


def response(email: str, access_key=None, database=None) -> tuple:
    """
    generates a response message to send back to the client
    :param email:
    :param access_key:
    :return: (response message, list of files)
    """
    files = return_list(email, database=database)
    files_string = ''
    for file in files:
        files_string += file['resource_path'] + '\r\n'

    code = None
    if len(files_string) > 0:
        code = codes.SUCCESS
    else:
        code = codes.NO_FILES_FOUND

    response_string = message_serializer.build_response_string(code, file_size=len(files_string), content=files_string.encode())
    return response_string, files_string.strip('\r\n')


def is_public(filename, database=None):
    """

    :param filename:
    :return: True if the file is public
    """
    public = False
    query = "SELECT public FROM Resources WHERE resource_path = %s"
    access = database.query(query, (filename,))

    public = access[0]['public'] == 1

    return public


def has_access(filename, email, database=None):
    """

    :param filename:
    :param email:
    :return: True if the user has access
    """
    access = False
    query = "SELECT resource_id FROM Resources where resource_path = %s"

    resource_id = database.query(query, (filename,))[0]['resource_id']

    query = "SELECT user_id FROM Users where email = %s"
    user_id = database.query(query, (email,))[0]['user_id']

    query = "SELECT access_id FROM Access where user_id=%s AND file_id=%s"
    info = (int(user_id), int(resource_id))

    key = database.query(query, info)

    access = len(key) > 0

    return access


def return_list(email, database=None) -> list[dict]:
    """
    A method that will return a list of files that are public or that the user owns
    :param
    :return: dict -> {
        'resource_id': int,
        'type': str,
        'resource_path': str,
        'upload_date': datetime.datetime(),
        'user_id': int,
        'public': bool
    }
    """

    users_query = "SELECT * FROM Users WHERE email = %s"
    users_parameters = (email,)
    users: list[dict] = database.query(users_query, users_parameters)

    if len(users) == 0:
        return []

    resources_query = "SELECT * FROM Resources WHERE public = 1"
    if users[0]['user_id']:
        resources_query = "SELECT * FROM Resources"
        # resources_parameters = (users[0]['user_id'],)
        rows = database.query(resources_query, ())
    else:
        rows = database.query(resources_query)

    list_to_return = []
    for row in rows:
        row['public'] = row['public'] == 1
        filename = row['resource_path']
        if row not in list_to_return and (is_public(filename, database) or has_access(filename, email, database)):
            list_to_return.append(row)

    return list_to_return
