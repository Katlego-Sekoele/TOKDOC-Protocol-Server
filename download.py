# sending a file to the client

import mysql.connector

db = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
)

cursor = db.cursor()


# checks if file name entered is valid
def valid_filename(filename):
    valid = False
    query = "SELECT resource_path FROM resources WHERE resource_path = %s"
    cursor.execute(query, filename)

    file_exists = cursor.fetchone()

    if file_exists is not None:
        valid = True

    return valid


# this method works when valid_filename is true
def check_permissions(filename):
    public = False
    query = "SELECT public FROM recourses WHERE resource_path = %s"
    cursor.execute(query, filename)
    access = cursor.fetchone()

    if access == "True":
        public = True

    return public


# checks if an access ID exists for the client
def check_access(filename, email):
    access = False
    query = "SELECT resource_id FROM resources where resource_path = %s"
    cursor.execute(query, filename)
    resource_id = cursor.fetchone()

    query = "SELECT user_id FROM resources where email = %s"
    cursor.execute(query, email)
    user_id = cursor.fetchone()

    query = "SELECT access_id FROM Access where user_id=%s AND resource_id=%s"
    info = (user_id, resource_id)
    cursor.execute(query, info)

    key = cursor.fetchone()

    if key is not None:
        access = True

    return access

# uploading the actual contents of the file to the client :)
# please kindly do this part Tiyani or Maesela
