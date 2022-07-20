
import psycopg2

class Server():
    def __init__(self, db_host, db_dbname, db_user, db_password):
        self.db_host = db_host
        self.db_dbname = db_dbname
        self.db_user = db_user
        self.db_password = db_password


        def connection_db(self,):
            conn = psycopg2.connect(dbname= self.db_dbname,
                                    user= self.db_user,
                                    password= self.db_password,
                                    host= self.db_host
                                    )

            connection = conn.cursor()
            return connection

        connection_db()

