#-*- coding:utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64),
                                            Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'自动登录')
    submit = SubmitField(u'登录')


class RegistrationForm(FlaskForm):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64),
                                            Email()])
    username = StringField(u'用户名', validators=[
    Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                    'Usernames must have only letters, '
                                    'numbers, dots or underscores')])
    password = PasswordField(u'密码', validators=[
        Required(), EqualTo('password2', message=u'两次输入密码不一致！')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'此邮箱已经注册过！')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'此用户名已经被使用！')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'旧密码', validators=[Required()])
    password = PasswordField(u'新密码', validators=[
        Required(), EqualTo('password2', message=u'两次输入密码不一致！')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'更改密码')

class PasswordResetRequestForm(FlaskForm):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), 
                                            Email()])
    submit = SubmitField(u'重置密码')

class PasswordResetForm(FlaskForm):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), 
                                            Email()])
    password = PasswordField(u'新密码', validators=[
        Required(), EqualTo('password2', message=u'两次输入密码不一致！')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'重置密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(u'未发现该邮箱！')

class ChangeEmailForm(FlaskForm):
    email = StringField(u'新的邮箱', validators=[Required(), Length(1, 64), 
                                                Email()])
    password = PasswordField(u'密码', validators=[Required()])
    submit = SubmitField(u'更改邮箱')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'此邮箱已经注册过！')







