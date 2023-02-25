# listing all the available files

import mysql.connector

# returns filename + date + type + type + protection

db = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
)

cursor = db.cursor()


def return_list():
    # name of the database has been changed to resources !
    query = "SELECT filepath, upload_date, type, access FROM Files WHERE email = %s AND password = %s"

    cursor.execute(query)

    rows = cursor.fetchall()

    for row in rows:
        print(row)


