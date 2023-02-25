# authenticating user logging in details and signing up users
# making use of Database and dictionaries

import database_manager as database


# register new
def register_user(email, password):
    done = False

    # sql command
    command = "INSERT INTO users (email, password) VALUES (%s, %s)"
    creds = (email, password)
    database.query(command, creds)
    done = True

    return done


# check member
def check_user(email, password):
    found = False

    # sql command
    command = "SELECT email FROM users WHERE email = %s AND password = %s"

    creds = (email, password)
    result = database.query(command, creds)

    valid = result

    if valid is not None:
        found = True

    return found
