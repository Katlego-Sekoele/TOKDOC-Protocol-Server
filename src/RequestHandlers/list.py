"""
 listing all the available files
"""
from Utilities import database_manager as database
from Utilities import message_serializer as message_serializer
from Utilities import message_parser as m_breaker
from Utilities import codes


def response(email: str, access_key=None) -> tuple:
    files = return_list(email)
    files_string = ''
    for file in files:
        files_string += file['resource_path'] + '\r\n'

    code = None
    if len(files_string) > 0:
        code = codes.SUCCESS

    response_string = message_serializer.build_response_string(code, access_key, len(files_string))
    return response_string, files_string.strip('\r\n')


def return_list(message) -> list[dict]:
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
    message = m_breaker.get_message_string(message)
    id = m_breaker.get_headers(message)['USER']
    users_query = "SELECT * FROM Users WHERE email = %s"
    users_parameters = (id,)
    users: list[dict] = database.query(users_query, users_parameters)

    if len(users) == 0:
        return []

    resources_query = "SELECT * FROM Resources WHERE public = 1"
    if users[0]['user_id']:
        resources_query = "SELECT * FROM Resources WHERE public = 1 OR user_id = %s"
        resources_parameters = (users[0]['user_id'],)
        rows = database.query(resources_query, resources_parameters)
    else:
        rows = database.query(resources_query)

    for row in rows:
        row['public'] = row['public'] == 1

    return rows
