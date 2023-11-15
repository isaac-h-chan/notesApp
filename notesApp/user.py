

class User():
    
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password

    def setUsername(self, new):
        self.username = new
    
    def setPassword(self, new):
        self.password = new   