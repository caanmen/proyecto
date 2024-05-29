import psycopg2
from psycopg2.extras import DictCursor
import os

class Database:
    def __init__(self, host, dbname, user, password, port):
        self.connection = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password,
            port=port
        )

    def get_cursor(self):
        return self.connection.cursor(cursor_factory=DictCursor)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()
