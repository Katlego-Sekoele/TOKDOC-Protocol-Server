"""
File containing utility methods to handle database connections and database
querying.
"""
import sqlite3

from dotenv import load_dotenv


class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Initiates a connection to the database.
        Should be called on server startup.
        """
        load_dotenv()

        if self.connection:
            print('A connection to the database has already been established')
            return

        self.connection = sqlite3.connect('database.db', check_same_thread=False)
        print(self.connection)
        self.cursor = self.connection.cursor()

        #     print(cursor.execute('''SELECT
        #     name
        # FROM
        #     sqlite_schema
        # WHERE
        #     type ='table' AND
        #     name NOT LIKE 'sqlite_%';''').fetchall())

        # connection = mysql.connector.connect(
        #     host=os.getenv("HOST"),
        #     database=os.getenv("DATABASE"),
        #     user=os.getenv("USERNAME"),
        #     password=os.getenv("PASSWORD"),
        #     ssl_ca=os.getenv("SSL_CERT")
        # )
        #
        # try:
        #     if connection.is_connected():
        #         cursor = connection.cursor()
        #     cursor.execute("select @@version ")
        #     version = cursor.fetchone()
        #     if version:
        #         print('Running version: ', version)
        #     else:
        #         print('Not connected.')
        # except Error as e:
        #     raise Exception("Error while connecting to MySQL", e)

    def query(self, query_template, query_values=None) -> list[dict]:
        """
        Query the database.
        Leave query_values as none if you do not wish to use query parameters
        :param query_template: A SQL query that may or may not contain parameters
        :param query_values: A tuple of values to be used as SQL query parameters
        :return: An array of dictionaries representing the rows returned from the query.
        """
        # get cursor
        cursor = self.cursor
        # execute query
        try:
            query_template = str(query_template).replace('%s', '?')
            cursor.execute(query_template, query_values)
            # get rows
            result_rows = cursor.fetchall()
        except Exception as e:
            print(e)
        # get field names
        try:
            field_names = [i[0] for i in cursor.description]
        except TypeError:
            return []

        # map field names to value in dictionary
        entry = dict()
        results = []
        for row in result_rows:
            entry = dict()
            i = 0
            for column_value in row:
                entry[field_names[i]] = column_value
                i += 1
            results.append(entry)

        return results

    def commit(self):
        """
        Save transactions to disk
        :return:
        """
        connection = self.connection
        if connection is not None:
            connection.commit()

    def disconnect(self):
        """
        Closes the database connection.
        Should be called on server shutdown.
        """
        connection = self.connection
        try:
            connection.close()
        except AttributeError:
            print('The database connection has already been closed.')
