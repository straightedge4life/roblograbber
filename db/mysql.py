import MySQLdb

class mysql :
    client = None
    host = '127.0.0.1'
    port = 3306
    user = 'root'
    passwd = ''
    db = 'roblograbber'
    charset = 'utf8'

    def __init__(self):
        self.client = MySQLdb.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            passwd = self.passwd,
            db = self.db,
            charset = self.charset
        )