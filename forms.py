from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, SubmitField   
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    login = StringField('Логин: ', validators = [DataRequired(), Length(min=4, max=100, message='Ты шо ебанутый? Где ты видел ник меньше 4 символов или больше 100? Вводи нормально нахуй!')])
    password = PasswordField('Пароль: ', validators = [DataRequired(), Length(min=4, max=100)])
    remainme = BooleanField('Запомнить', default = False)
    submit = SubmitField('Войти')
    
class RegistrationForm(FlaskForm):
    login = StringField('Логин: ', validators=[DataRequired(), Length(min=4, max=100, message='Алло, обезьяна. От 4 и до 100 символов. Крутые имена типа Ли для крутых парней, а ты пока ебаное никто! Не выёбывайся!')])
    email = StringField('Email: ', validators=[
    DataRequired(message='Ну конечно же обязательно для заполнения, а ты как думал? Мы серьёзная организация!'),
    Email(message='Алло, даун сука, ты что не знаешь в 21 веке как имейлы выглядят???')
    ])
    password = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=6, max=20, message='Ну от 6 до 20 символов ебана! Придумай пароль, чтобы тебя не взломали и ты не заёбывал стражу со своими проблемами, обезьяна ебана!')])
    password_repeat = PasswordField('Повтор пароля: ', validators=[DataRequired(), EqualTo('password', message='Сука, ну ты издеваешься? Набери сосисками своими ебаными ОДИНАКОВЫЕ сука ОДИНАКОВЫЕ пароли для двух полей олень блять')])
    submit = SubmitField('Создать аккаунт')
    
    