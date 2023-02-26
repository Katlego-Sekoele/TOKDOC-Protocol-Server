# sending a file to the client
from socket import *

from src.Utilities import database_manager as database


# checks if file name entered is valid
def valid_filename(filename):
    valid = False
    query = "SELECT resource_path FROM resources WHERE resource_path = %s"
    results = database.query(query, filename)

    file_exists = results

    if file_exists is not None:
        valid = True

    return valid


# this method works when valid_filename is true
def check_permissions(filename):
    public = False
    query = "SELECT public FROM recourses WHERE resource_path = %s"
    access = database.query(query, filename)

    if access == "True":
        public = True

    return public


# checks if an access ID exists for the client
def check_access(filename, email):
    access = False
    query = "SELECT resource_id FROM resources where resource_path = %s"

    resource_id = database.query(query, filename)[0]

    query = "SELECT user_id FROM resources where email = %s"
    user_id = database.query(query, email)[0]

    query = "SELECT access_id FROM Access where user_id=%s AND resource_id=%s"
    info = (user_id, resource_id)

    key = database.query(query, info)

    if key is not None:
        access = True

    return access


# uploading the actual contents of the file to the client :)
def send(filename, serverSocket):
    file = open(filename, "rb")
    file_size = os.path.getsize(filename)

# to be replaced with message generator
    serverSocket.send(filename.encode())
    serverSocket.send(str(file_size).encode)

    data = file.read()

    toSend = {
        "file_size": file_size,
        "file_name": filename,
        "whatever maesela wants": 0,
        "bytes": data
    }

    serverSocket.sendall(data)

    serverSocket.send(b"<END>")

    file.close()

# please kindly do this part Tiyani or Maesela
