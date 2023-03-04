"""
 listing all the available files
"""
from src.Utilities import database_manager as database
from src.Utilities import message_parse as m_breaker


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
