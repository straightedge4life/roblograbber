import MySQLdb

class connector :
    host = 'localhost'
    port = 3006
    user = 'root'
    passwd = ''
    db = 'forge'
    charset = 'utf-8'
    def __init__(self , host , user , passwd , db , port = 3306 ,  charset = 'utf-8'):
        self.host = host
        self.user = user
        self.passwd = passwd 
        self.db = db
        self.charset = charset
        self.port = port
        return 

    def connet(self):
        conn = MySQLdb.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            passwd = self.passwd,
            db = self.db,
        )
        print(conn)
        return conn
