# listing all the available files

import database_manager as database


def return_list():
    query = "SELECT resource_path, upload_date, type, public FROM Resources"

    rows = database.query(query)

    return rows
