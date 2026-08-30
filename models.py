from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Main_menu(db.Model):
    __tablename__ = 'main_menu'
    
    id = db.Column(db.Integer, primary_key = True)
    menu_item = db.Column(db.String(100), nullable = False, unique = True)
    menu_item_url = db.Column(db.String(100), nullable = False, unique = True)
    
    def __repr__ (self) -> str:
        return f'<Menu {self.menu_item}>'
    
    
class Posts(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key = True)
    post_title = db.Column(db.String(200), nullable = False, unique = True)
    post_category = db.Column(db.String(200))
    post_url = db.Column(db.String(200))
    post_content = db.Column(db.String(10_000))
    created_at = db.Column(db.DateTime, default = lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Menu {self.post_title}>'

class Users(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key = True)
    user_login = db.Column(db.String(300), nullable = False, unique = True)
    user_email = db.Column(db.String(300), nullable = False, unique = True)
    user_password = db.Column(db.String(300), nullable = False)
    created_at = db.Column(db.DateTime, default = lambda: datetime.now(timezone.utc))
    avatar = db.Column(db.String(300), nullable = True)
    


    