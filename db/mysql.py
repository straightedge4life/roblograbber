import MySQLdb


class Mysql:
    client = None
    host = '127.0.0.1'
    port = 3306
    user = 'root'
    pass_code = ''
    db = 'roblograbber'
    charset = 'utf8'

    def __init__(self):
        self.client = MySQLdb.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.pass_code,
            db=self.db,
            charset=self.charset
        )
