from flask_wtf import Form
#from flask import session, g
from wtforms import StringField, IntegerField, BooleanField, TextAreaField, HiddenField, validators
from wtforms.validators import DataRequired, Length
from wtforms.fields.html5 import EmailField

    
class LoginForm(Form):
    #openid = StringField('openid', validators=[DataRequired()])
    test_code =  StringField('test_code')
    email = EmailField('email',validators=[DataRequired(), validators.Email()])
    remember_me = BooleanField('remember_me', default=False)



    
class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        reguser = Reguser.query.filter_by(nickname=self.nickname.data).first()
        if reguser is not None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True

class CourseForm(Form):
    title = StringField('title', validators=[DataRequired()])
    #body = StringField('body', validators=[DataRequired()])
    level = IntegerField('level', validators=[DataRequired()])
    #sbj1 =  StringField('sbj1')
    #sbj2 =  StringField('sbj2')
    #sbj3 =  StringField('sbj3')
    
    id = HiddenField()

class MeetingForm(Form):
    id = HiddenField()
    title = StringField('title', validators=[DataRequired()])
    course_id = IntegerField('course_id', validators=[DataRequired()])
    prompt = StringField('prompt')
    note =  TextAreaField('note')
    close_opt = IntegerField('close_opt')
    live_till_month = IntegerField('live_till_month')
    live_till_days = IntegerField('live_till_days')
    live_till_hours = IntegerField('live_till_hours')

class MuddyForm(Form):
    body = TextAreaField('body', validators=[Length(min=0, max=300)])
    #body = StringField('body')
    meeting_id = IntegerField('meeting_id', validators=[DataRequired()])
    #meeting_id = IntegerField('meeting_id')
    id = HiddenField()

class ChangeIndexForm(Form):
    id = HiddenField()


class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])


class EmailForm(Form):
    id = HiddenField()
    #test_code =  StringField('test_code')
    email = EmailField('email', validators=[validators.Email()])

class GenForm(Form):
    id = HiddenField()
    inp_string =  StringField('string', validators=[DataRequired()])
