from db.connector import connector
client = None

class mysql :
    def __init__(self):
        self.client = connector(host = 'localhost' , user = 'root' , passwd = '' , db = 'roblograbber')
        self.client = self.client.connet()