#-*- coding:utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp
from ..models import Role, User, Category
from flask_pagedown.fields import PageDownField

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    location = StringField(u'所在地', validators=[Length(0, 64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'提交')

class EditProfileAdminForm(FlaskForm):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 
                                        'Username must have only letters, '
                                        'number, dots or underscores')])
    confirmed = BooleanField(u'账户认证')
    role = SelectField(u'权限', coerce=int)
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    location = StringField(u'所在地', validators=[Length(0, 64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                            for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.date).first():
            raise ValidationError('Emai already registered.')

    def validate_username(self, field):
        if field.data !=self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

            
class PostForm(FlaskForm):
    title = StringField(u'标题', validators=[Required()])
    body = PageDownField(u'内容', validators=[Required()])
    summury = PageDownField(u'摘要', validators=[Required()])
    category = SelectField(u'分类',coerce=int)
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category 
            in Category.query.order_by(Category.name).all()]
        
class CommentForm(FlaskForm):
    body = PageDownField(u'留言', validators=[Required()])
    submit = SubmitField(u'提交')





