from flask import Blueprint, request, redirect, render_template, session, flash, url_for
from models import Posts, Users, db

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


menu = [{'title' : 'Главная', 'url' : '.index'},
        {'title' : 'Войти', 'url' : '.login'},
        {'title' : 'Выйти', 'url' : '.logout'},
        {'title' : 'Список постов', 'url' : '.list_pub'},
        {'title' : 'Список пользователей', 'url' : '.list_users'}]

@admin.route('/')
@admin.route('/index')
def index():
    if not is_logged():
        return redirect(url_for('.login'))
    else:
        return render_template('admin/index.html', menu=menu)
    
def login_admin():
    session['admin_logged'] = 1    
    
def is_logged():
    return True if session.get('admin_logged') == 1 else False

def logout_admin():
    session.pop('admin_logged', None)
    
@admin.route('/login', methods=['POST', 'GET'])
def login():
    if is_logged():
        return redirect(url_for('.index'))
    else:
        if request.method == 'GET':
            return render_template('admin/login.html', menu=menu)
        elif request.method == 'POST':
            if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
                login_admin()
                flash('Добро пожаловать, администратор!', category='success')
                return redirect(url_for('.index'))
            else:
                flash('Неверный ввод данных! Попробуйте ещё раз', category='error')
                return render_template('admin/index.html', menu = menu)
            
            
@admin.route('/logout')
def logout():
    if not is_logged():
        return redirect(url_for('.login'))
    else:
        logout_admin()
        return redirect(url_for('.login'))
    
    
@admin.route('/list_pub')
def list_pub():
    list = []
    
    try:
        list = Posts.query.all()
        print('Список постов получен!')
    except:
        print('Список постов не получен!')
    
    return render_template('admin/list_pub.html', menu=menu, posts=list)


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
def show_user(user_id):
    if is_logged():
        try:
            user = Users.query.get(user_id)
        except:
            print('Пользователь не найден')
        
        return render_template('admin/user_detail.html', menu=menu, user=user)
    else:
        return redirect(url_for('admin.login'))

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
    
