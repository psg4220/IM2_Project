import mysql.connector
from mysqlx.errors import OperationalError
import Variables


class DatabaseManager:

    def __init__(self):
        self.database = mysql.connector.connect(
            host=Variables.HOST,
            user=Variables.USER,
            password=Variables.PASSWORD,
            database=Variables.DATABASE
        )
