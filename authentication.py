# authenticating user logging in details and signing up users
# making use of Database and dictionaries

import mysql.connector
import hashlib

db = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
)

cursor = db.cursor()


# register new
def register_user(email, password):
    done = False

    # sql command
    command = "INSERT INTO users (email, password) VALUES (%s, %s)"
    cred = (email, password)
    cursor.execute(command, cred)
    done = True

    return done


# check member
def check_user(email, password):
    found = False

    # sql command
    command = "SELECT email FROM users WHERE email = %s AND password = %s"

    creds = (email, password)
    cursor.execute(command, creds)

    valid = cursor.fetchone()

    if valid is not None:
        found = True

    return found
