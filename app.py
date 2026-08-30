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

app = Flask(__name__)

app.register_blueprint(admin, url_prefix = '/admin')

app.config.from_object(DevConfig)

login_manager = LoginManager(app=app)
login_manager.login_view = 'login'
login_manager.login_message = 'Вы не авторизованы'
login_manager.login_message_category = 'error'



db.init_app(app=app)


@app.route('/show_config')
def show_config():
    return f'''
            'SECRET_KEY' : {app.config['SECRET_KEY']}, 
            'SQLALCHEMY_DATABASE_URI' : {app.config['SQLALCHEMY_DATABASE_URI']}, 
            'DEBUG' : {app.config['DEBUG']}, 
            'SQLALCHEMY_TRACK_MODIFICATIONS' : {app.config['SQLALCHEMY_TRACK_MODIFICATIONS']}, 
    '''

@app.route('/test_db')
def test_db():
    try:
        db.engine.connect()
        return 'База данных подключена!'
    except:
        return 'База данных не подключена!'


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



@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:    
        return redirect(url_for('profile', username=current_user.get_username()))
    else:
        form = LoginForm()
        
        if request.method == 'GET':
            return render_template('login.html', menu=menu, title='Вход в аккаунт', hero_text='Войти в аккаунт', form=form)
        elif request.method == 'POST':
            
            
            if form.validate_on_submit():
                
                user_login = form.login.data
                user_password = form.password.data
                
                user = Users.query.filter_by(user_login=user_login).first()
                
                if user:
                    if check_password_hash(user.user_password, user_password):
                        logined_user = UserLogin().create(user)
                        rm = form.remainme.data
                        login_user(logined_user, remember=rm)
                        
                        return redirect(request.args.get('next') or url_for('profile', username=user.user_login))
                    else:
                        flash('Проверьте правильность ввода!', category='error')
                        return render_template('login.html', menu=menu, title='Войти в аккаунт', hero_text='Вход в аккаунт', form=form)
                else:
                    flash('Пользователь не существует! Зарегистрируйте аккаунт!', category='error')
                    return redirect(url_for('registration'))
            else:
                flash('Некорректный ввод данных', category='error')
                return render_template('login.html', menu=menu, title='Вход в аккаунт', hero_text='Войти в аккаунт', form=form)
                
        

# выход из профиля
@app.route('/logout')
def logout():
    logout_user()
    return f'Вы больше не авторизованы'
            
    

@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('profile', username=current_user.get_username()))
    else:
        form = RegistrationForm()
        
        if request.method == 'GET':
            return render_template('registration.html', menu=menu, title='Регистрация аккаунта', hero_text='Зарегистрируйтесь чтобы играть', form=form)
        elif request.method == 'POST':
            
            if form.validate_on_submit():
                user_login = form.login.data
                user_email = form.email.data
                user_password = form.password.data
                
                existing_user = Users.query.filter_by(user_login=user_login).first()
                
                if existing_user:
                    flash('Пользователь уже зарегистрирован! Выберите другое имя!', category='error')
                    return render_template('registration.html', menu=menu, title='Регистрация аккаунта', hero_text='Зарегистрируйтесь чтобы играть')
                else:
                    db.session.add(Users(user_login = user_login, user_email = user_email, user_password = generate_password_hash(user_password)))
                    db.session.commit()
                    
                    flash('Пользователь зарегистрирован! Добро пожаловать в долину рудников!', category='success')
                    return redirect(url_for('profile', username=user_login))

        
    
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




# РАБОТАЕМ С ПОСТАМИ
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
                
# показать пост
@app.route('/show_post/<post_url>')
@login_required
def show_post(post_url):
    post = Posts.query.filter_by(post_url = post_url).first()
    
    return render_template('post.html', title=f'Долина рудников ~ {post.post_title} ~', menu=menu, post = post)
    



# Делаем ответы сервера
@app.route('/test_response')
def test_response():
    content = render_template('index.html', menu=menu, title='title', hero_text = 'hero_text', posts = Posts.query.all())
    res = make_response(content)
    
    res.headers['Content-Type'] = 'text/plain'
    res.headers['Server'] = 'flasksite'
    
    return res

@app.route('/test_response2')
def test_response2():
    res = '<h1>Страница недоступна</h1>'
    
    return res

# @app.errorhandler(404)
# def page_not_found(error):
#     return ('Страница недоступна', 404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')


@app.route('/test_response3')
def test_response3():
    return ('<h1>Something page</h1>', 200, {'Content-Type' : 'text/plain'})

@app.route('/transfer')
def transfer():
    return redirect(url_for('index'), 301)


print('initialization app')
print()

@app.before_request
def before_request():
    print('before_request() is called()')
    print()


    
@app.after_request
def after_requset(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
    
    # res = response
    # res.headers['Content-Type'] = 'text/html; charset=utf-8'
    # res.headers['Server'] = 'flasksite'
    
    # return res

@app.teardown_request
def teardown_request(exception = None):
    print(f'teardown_request() is called, exception: {exception}')
    print()
    

#работаем с cookie
@app.route('/test_login')
def test_login():
    log = ''
    
    if request.cookies.get('logged'):
        log = request.cookies.get('logged')
    
    res = make_response(f'<h1>Страница авторизации</h1> logged: {log}')
    
    res.set_cookie('logged', 'yes')
    
    return res

@app.route('/test_logout')
def test_logout():
    res = make_response('<h1>Вы больше не авторизованы</h1>')
    
    res.set_cookie('logged', '', 0)
    
    return res



# работаем с сессиями
@app.route('/test_session')
def test_session():
    if 'visits' in session:
        session['visits'] += 1
    else:
        session['visits'] = 1
        
    return f'Количество заходов: {session['visits']}'

data = [1, 2, 3, 4, 5]
@app.route('/test_data')
def test_data():
    if 'data' in session:
        session['data'][1] += 1
        session.modified = True
    else:
        session['data'] = data
    
    return f'''session['data'] = {session['data']}'''


if __name__ == '__main__':
    app.run(debug=True)
    
with app.test_request_context():
    print(url_for('index'))
    print(url_for('about_us'))
    print(url_for('contact_us'))



