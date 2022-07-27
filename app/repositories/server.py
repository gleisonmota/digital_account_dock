import psycopg2

class ConnectionDb():
    def __init__(self, db_host, db_dbname, db_user, db_password):
        self.db_host = db_host
        self.db_dbname = db_dbname
        self.db_user = db_user
        self.db_password = db_password

    def postgre_sql(self):
        conn = psycopg2.connect(
                                host = self.db_host,
                                dbname = self.db_dbname,
                                user = self.db_user,
                                password = self.db_password
                                )

        return conn.cursor()