from flask import Blueprint, request, redirect, render_template, session, flash, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from UserLogin import UserLogin
from models import Posts, Users, db
from forms import LoginAdmin
from werkzeug.security import check_password_hash


admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


menu = [{'title' : 'Главная', 'url' : '.index'},
        {'title' : 'Войти', 'url' : '.login'},
        {'title' : 'Выйти', 'url' : '.logout'},
        {'title' : 'Список постов', 'url' : '.list_pub'},
        {'title' : 'Список пользователей', 'url' : '.list_users'}]

@admin.route('/')
@admin.route('/index')
@login_required
def index():
        return render_template('admin/index.html', menu=menu)
    

@admin.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginAdmin()
    if request.method == 'GET':
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin.index'))
            else:
                flash('Вы не администратор! Доступ в админ-панель для вас закрыт.', category='error')
                return render_template('admin/login.html', menu=menu, form=form)   
        return render_template('admin/login.html', menu=menu, form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            login = form.login.data
            password = form.password.data
            
            existing_user = Users.query.filter_by(user_login = login).first()
            
            if existing_user and existing_user.is_admin:
                if check_password_hash(existing_user.user_password, password):
                    logined_user = UserLogin().create(existing_user)
                    login_user(logined_user)
                    
                    flash('Добро пожаловать, администратор!', category='success')
                    return redirect(url_for('admin.index'))
                else:
                    flash('Неправильный пароль! Попробуйте ещё раз', category='error')
                    return render_template('admin/login.html', menu=menu, form=form)
            else:
                flash('Пользователь не найден или пользователь не является админстратором. Попробуйте авторизоваться как обычный игрок.', category='error')
                return render_template('admin/login.html', menu=menu, form=form)
        else:
            flash('Неправильный ввод данных', category='error')
            return render_template('admin/login.html', menu=menu, form=form)
        
        
@admin.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('admin.login'))
    else:
        return redirect(url_for('admin.login'))
    
    
@admin.route('/list_pub')
def list_pub():
    list = []
    
    try:
        list = Posts.query.all()
        print('Список постов получен!')
    except:
        print('Список постов не получен!')
    
    return render_template('admin/list_pub.html', menu=menu, posts=list)


@admin.route('/show_post/<post_id>')
def show_post(post_id):
    try:
        existing_post = Posts.query.get(post_id)
    except:
        print('Пост не найден!')
    
    return render_template('admin/post_detail.html', menu=menu, post = existing_post)    

@admin.route('/delete_post/<post_id>', methods=['POST', 'GET'])
def delete_post(post_id):
    try:
        post = Posts.query.get(post_id)
        
        db.session.delete(post)
        db.session.commit()
    except:
        print('Такого поста не существует!')

    return redirect(url_for('admin.list_pub'))


@admin.route('/list_users')
def list_users():
    list = []
    try:
        list = Users.query.all()
        print('Список пользователей получен')
    except:
        print('Список пользователей не получен')
        
    return render_template('admin/list_users.html', menu=menu, users=list)

@admin.route('/show_user/<user_id>')
@login_required
def show_user(user_id):
        try:
            user = Users.query.get(user_id)
        except:
            print('Пользователь не найден')
        
        return render_template('admin/user_detail.html', menu=menu, user=user)

@admin.route('/make_admin/<user_id>', methods=['POST'])
def make_admin(user_id):
    try:
        user = Users.query.get(user_id)
    except: 
        print('Пользователь не найден')
        
    if not user.is_admin:
       user.is_admin = True 
    else:
        user.is_admin = False
        
    db.session.commit()
    
    return redirect(url_for('admin.show_user', user_id = user_id))
    
