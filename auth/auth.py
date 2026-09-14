from flask import Blueprint, request, render_template, flash, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from UserLogin import UserLogin
from models import Users, Main_menu, db
from forms import RegistrationForm, LoginForm




auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')




@auth.route('/registration', methods=['POST', 'GET'])
def registration():
    menu = Main_menu.query.all()
    if current_user.is_authenticated:
        return redirect(url_for('profile', username = current_user.get_username()))
    else:    
        form = RegistrationForm()
        if request.method == 'GET':
            return render_template('auth/registration.html', menu = menu, title='Зарегистрируйся чтобы играть', hero_text =     'Регистрация', form=form)
        elif request.method == 'POST':
            if form.validate_on_submit():
                
                existing_user = Users.query.filter_by(user_login=form.login.data).first()
                if existing_user:
                    flash('Такой пользователь уже существует! Придумайте другой никнейм', category='error')
                    return render_template('auth/registration.html', menu = menu, title='Зарегистрируйся чтобы играть', hero_text = 'Регистрация аккаунта', form=form)
                else:
                    user_login = form.login.data
                    user_email = form.email.data
                    user_password = generate_password_hash(form.password.data)
            
                    db.session.add(Users(user_login = user_login, user_email = user_email, user_password = user_password))
                    db.session.commit()
            
            
                    user = Users.query.filter_by(user_login = user_login).first()
            
            
                    logined_user = UserLogin().create(user)
                    login_user(logined_user)
            
                    flash(f'Добро пожаловать, {user_login}')
                    return redirect(url_for('profile', username = user.user_login))  
            else:
                flash('Некорректные данные. Проверьте правильность ввода.', category='error')
                return render_template('auth/registration.html', menu = menu, title='Зарегистрируйся чтобы играть', hero_text = 'Регистрация', form=form)
            
            
@auth.route('/login', methods=['POST', 'GET'])
def login():
    menu = Main_menu.query.all()
    if current_user.is_authenticated:
        return redirect(url_for('profile', username=current_user.get_username()))
    else:
        form = LoginForm()
        if request.method == 'GET':
            return render_template('auth/login.html', menu=menu, title='Войдите чтобы играть', hero_text='Вход в аккаунт', form=form)
        elif request.method == 'POST':
            if form.validate_on_submit():
                user_login = form.login.data
                user_password = form.password.data
                
                user = Users.query.filter_by(user_login = user_login).first()
                
                if check_password_hash(user.user_password, user_password):
                    logined_user = UserLogin().create(user)
                    rm = True if form.remainme.data else False
                    login_user(logined_user, remember=rm)
                    
                    flash(f'Добро пожаловать {user_login}', category='success')
                    return redirect(request.args.get('next') or url_for('profile', username=user_login))
            else:
                flash('Проверьте правильность ввода!', category='error')
                return render_template('auth/login.html', menu=menu, title='Войдите чтобы играть', hero_text='Вход в аккаунт', form=form)  
                
                
@auth.route('/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('.login'))
    else:
        logout_user()
        return f'Вы больше не авторизованы'
        
                