#!/Python27/python

import pymysql
import settings

# Class used for opening and closing database connection


class Database:

    # get settings from settings.py
    def __init__(self):
        self.host = settings.mysql_host
        self.port = settings.mysql_port
        self.user = settings.mysql_user
        self.passwd = settings.mysql_passwd
        self.schema = settings.mysql_schema

    # return a new connection
    def start_connection(self):
        return pymysql.connect(host=self.host,
                               user=self.user,
                               password=self.passwd,
                               db=self.schema,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)

    # close a connection
    @staticmethod
    def close_connection(connection):
        connection.close()
