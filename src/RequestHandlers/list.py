# listing all the available files


from Utilities import database_manager as database


def return_list(email: str) -> list[dict]:

    users_query = "SELECT * FROM Users WHERE email = %s"
    users_parameters = (email,)
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

    return rows
