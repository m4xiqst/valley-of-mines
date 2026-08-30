from sqlalchemy import delete
from models import db, Main_menu
from app import app

menu = [
    {'menu_item' : 'Главная', 'menu_item_url' : '/index'},
    {'menu_item' : 'Войти', 'menu_item_url' : '/login'},
    {'menu_item' : 'Профиль', 'menu_item_url' : '/profile'},
    {'menu_item' : 'О нас', 'menu_item_url' : '/about_us'},
    {'menu_item' : 'Связаться с нами', 'menu_item_url' : '/contact_us'},
    {'menu_item' : 'Добавить пост', 'menu_item_url' : '/add_post'}
]

with app.app_context():
    db.session.execute(delete(Main_menu))
    db.session.commit()
    
    for i in range(len(menu)):
        item = Main_menu(menu_item = menu[i]['menu_item'], menu_item_url=menu[i]['menu_item_url'])
        db.session.add(item)
        
    db.session.commit()
    
    print('Main menu was refreshed!')
    
    