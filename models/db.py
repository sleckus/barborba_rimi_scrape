import mysql.connector


class DB():
    def __init__(self):
        self.connectDB()
    def connectDB(self):
           self.conn = mysql.connector.connect(
               host="127.0.0.1",  # localhost
               user='root',
               password='',  # rašot savo
               database="supermarkets"  # rašot savo
           )

    def close(self):
        self.conn.close()