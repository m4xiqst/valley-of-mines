class UserLogin:
    def from_db(self, user_id):
        self.__user = Users.query.get(user_id)
        
        return self
    
    def create(self, user):
        
        self.__user = user
        
        return self
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.__user.id)
    
    def get_username(self):
        return str(self.__user.user_login)
    
    def get_email(self):
        return str(self.__user.user_email)
    
    def is_admin(self):
        return str(self.__user.is_admin)