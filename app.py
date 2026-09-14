import os
import time
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, url_for, flash, request, redirect, abort, session, make_response
from models import db, Main_menu, Posts, Users
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from UserLogin import UserLogin
from config import DevConfig
from forms import LoginForm, RegistrationForm

from admin.admin import admin
from auth.auth import auth

app = Flask(__name__)

# Blueprints
app.register_blueprint(admin, url_prefix = '/admin')
app.register_blueprint(auth, url_prefix = '/auth')

app.config.from_object(DevConfig)

login_manager = LoginManager(app=app)
login_manager.login_view = 'login'
login_manager.login_message = 'Вы не авторизованы'
login_manager.login_message_category = 'error'



db.init_app(app=app)


with app.app_context():
    db.create_all()
    
    menu = Main_menu.query.all()
    
    print('Tables were created!')



# главвная
@app.route('/index')
@app.route('/')
def index():
    
    posts_lists = Posts.query.all()
    
    return render_template('index.html', title = 'Готика: Долина Рудников. Главная страница', menu = menu, hero_text = 'Добро пожаловать в долину рудников!', posts = posts_lists)

       
# выход из профиля
@app.route('/logout')
def logout():
    logout_user()
    return f'Вы больше не авторизованы'
            
    
# работаем с пользователями
@app.login_manager.user_loader
def load_user(user_id):
    user = Users.query.get(user_id)
    
    if user:
        return UserLogin().create(user=user)
    else:
        return None

#профиль
@app.route('/profile/<username>')
def profile(username):
    user = Users.query.filter_by(user_login = username).first()
    return render_template('profile.html', username = username, user = user, menu=menu, title = f'Профиль игрока {username}', hero_text = f'Добро пожаловать в Долину Рудников {username}')

# Загружаем аватар
@app.route('/upload_avatar', methods=['POST', 'GET'])
@login_required
def upload_avatar():
    # 1. Проверяем, есть ли файл в запросе
    if 'avatar' not in request.files:
        flash('Файл не выбран!', category='error')
        return redirect(url_for('profile', username=current_user.get_username()))
    
    file = request.files['avatar']
    
    # 2. Проверяем, что файл не пустой
    if file.filename == '':
        flash('Файл не выбран!', category='error')
        return redirect(url_for('profile', username = current_user.get_username()))
    
    
    # 3. Проверяем расширение файла (берём из конфига)
    allowed_extensions = app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
    
    if '.' not in file.filename or file.filename.rsplit('.',1)[1].lower() not in allowed_extensions:
        flash('Недопустиммый формат!', category='error')
        return redirect(url_for('profile', username = current_user.get_username()))
        
    
    # 4. Генерируем уникальное имя файла
    user_id = current_user.get_id()
    original_name = secure_filename(file.filename)
    filename = f'{user_id}_{int(time.time())}_{original_name}'
    
    
    # 5. Получаем путь к папке аватарок
    upload_folder = app.config['UPLOAD_FOLDERS']['avatars']
    
    # 6. Сохраняем файл
    file.save(os.path.join(upload_folder, filename))
    
    # 7. Обновляем запись в БД
    user = Users.query.get(int(user_id))
    user.avatar = filename
    db.session.commit()
    
    flash('Аватар успешно загружен!', category='success')
    return redirect(url_for('profile', username = current_user.get_username()))


#удаляем аватар
@app.route('/delete_avatar', methods=["POST"])
@login_required
def delete_avatar():
    user_id = current_user.get_id()
    user = Users.query.get(int(user_id))
        
    # Проверяем, есть ли аватарка
    if not user.avatar:
        flash('У тебя нет аватарки для удаления!', category='error')
        return redirect(url_for('profile', username=current_user.get_username()))
    else:
        avatar_path = os.path.join(app.config['UPLOAD_FOLDERS']['avatars'], user.avatar)
            
        if os.path.exists(avatar_path):
            os.remove(avatar_path)
                
        # Очищаем поле в БД
        user.avatar = None
        db.session.commit()
            
        flash('Аватарка удалена!', category='success')
        return redirect(url_for('profile', username = current_user.get_username()))
      

@app.route('/profile2')
def profile2():
    return f'''<p><a href={url_for('logout')}>Выйти из профиля</a></p>
                user info: {current_user.get_id()}'''


# о нас
@app.route('/about_us')
def about_us():
    print(url_for('about_us'))
    return render_template('about_us.html', title = 'Готика: Долина Рудников. О команде проекта.', menu = menu, hero_text = 'О нашей команде')




# форма братной связи
@app.route('/contact_us', methods=['POST', 'GET'])
def contact_us():

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        message = request.form.get('message', '').strip()
        
        # ===== ВАЛИДАЦИЯ =====
        if not name:
            flash('⚠️ Имя обязательно для заполнения!', category='error')  # <-- 'error' - ЭТО КАТЕГОРИЯ
        elif len(name) < 2:
            flash('⚠️ Имя слишком короткое!', category='error')
        elif not email or '@' not in email:
            flash('⚠️ Введите корректный email!', category='error')
        elif not message:
            flash('⚠️ Напишите комментарий!', category='error')
        else:
            flash('✅ Сообщение успешно отправлено!', category='success')  # <-- 'success' - ЭТО КАТЕГОРИЯ
            
    return render_template('contact_us.html', menu = menu, hero_text='Связаться с долиной рудников')



# добавить пост
@app.route('/add_post', methods=['POST', 'GET'])
def add_post():
    if request.method == 'GET':
        return render_template('add_post.html', menu=menu, title = 'Долина Рудников: Добавить пост', hero_text = 'Добавить пост')
    
    elif request.method == 'POST':
        
        post_title = request.form['title']
        post_category = request.form['category']
        post_url = request.form['post_url']
        post_content = request.form['content']
        
        existing_post = Posts.query.filter_by(post_url = post_url).first()
        
        if existing_post:
            flash('Post is already added ⚠️', category='error')
            
            return render_template('add_post.html', menu=menu, title = 'Долина Рудников: Добавить пост', hero_text = 'Добавить пост')
        
        else:
            
            if len(post_title) > 5 and len(post_content) > 200:
                db.session.add(Posts(post_title = post_title, post_category = post_category, post_url = post_url, post_content = post_content))
                db.session.commit()
                
                flash('Post was added ✅', category='success')
                return render_template('add_post.html', menu=menu, title = 'Долина Рудников: Добавить пост', hero_text = 'Добавить пост')
            
            else:
                flash ('''Post wasn't added ❌. Something wrong with lenght of title or content''', category='error')
                return render_template('add_post.html', menu=menu, title = 'Долина Рудников: Добавить пост', hero_text = 'Добавить пост')
                
# показать пост
@app.route('/show_post/<post_url>')
@login_required
def show_post(post_url):
    post = Posts.query.filter_by(post_url = post_url).first()
    
    return render_template('post.html', title=f'Долина рудников ~ {post.post_title} ~', menu=menu, post = post)
    

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')


    
@app.after_request
def after_requset(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
    

@app.teardown_request
def teardown_request(exception = None):
    print(f'teardown_request() is called, exception: {exception}')
    print()
    


if __name__ == '__main__':
    app.run(debug=True)




