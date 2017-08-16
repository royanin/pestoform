from hashlib import md5
from app import db
from app import app
from datetime import datetime,timedelta
from flask import g
import string, random
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_social import Social, SQLAlchemyConnectionDatastore

import sys
if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True
    import flask_whooshalchemy as whooshalchemy

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    #__tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    #social_id = db.Column(db.String(64), nullable=False, unique=True)
    social_nw = db.Column(db.String(64))
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(255), index=True, nullable=True, unique=True)
    password = db.Column(db.String(255), nullable=True)
    courses = db.relationship('Course', backref='user',lazy='dynamic', cascade="all, delete-orphan")
    all_meetings = db.relationship('Meeting', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    all_muddies = db.relationship('Muddy', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    active = db.Column(db.Boolean())
    #about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    affiliation = db.Column(db.String(120))
    #edu_lvl = db.Column(db.String(5))
    #location =  db.Column(db.String(140))
    #rel_con = db.relationship('Post', backref='author', lazy='dynamic')
    roles = db.relationship('Role', secondary=roles_users,backref=db.backref('users', lazy='dynamic'))

    '''

    def __init__(self, nickname, email, password):
        self.email = email
        self.password
        self.nickname = make_unique_nickname(email.split('@')[0])
        
    
    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)
    '''    
    
    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname


    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    #def avatar(self, size):
        #return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % \
            #(md5(self.email.encode('utf-8')).hexdigest(), size)


    def __repr__(self):
        return '<User %r>' % (self.nickname)
'''
class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    provider_id = db.Column(db.String(255))
    provider_user_id = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    secret = db.Column(db.String(255))
    display_name = db.Column(db.String(255))
    profile_url = db.Column(db.String(512))
    image_url = db.Column(db.String(512))
    rank = db.Column(db.Integer)
'''

class Course(db.Model):
    __searchable__ = ['title','sbj1', 'sbj2', 'sbj3']

    id = db.Column(db.Integer, primary_key=True)
    title =  db.Column(db.String(140))
    type_course = db.Column(db.Integer) #0: traditional course, 1: seminar 2: event 3: workshop etc.
    level =  db.Column(db.Integer)   #0: none, 1-3: K-12, 4-UGL 5-UGU 6-grad, 7-LLL, 8-Service Learning 
    sbj1 =  db.Column(db.String(100))  #think of making this into disciplines/sub-dis
    sbj2 =  db.Column(db.String(100))
    sbj3 =  db.Column(db.String(100))
    timestamp = db.Column(db.DateTime)
    #live_till =  db.Column(db.DateTime) #0: datetime- 6-months -- the course will be archived after that, 1: never, 2: now 3: 1 week, 4: 3-months, 5: year
    live_stat = db.Column(db.Boolean) #True:live, False:archived
    #del_stat = db.Column(db.Boolean) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    meetings = db.relationship('Meeting', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    note = db.Column(db.String(500))
    #parent_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    #children = db.relationship("Post")

    #rel_cont = db.nothing done yet

    def __init__(self,title,level):
        self.title = title
        self.timestamp = datetime.utcnow()
        self.live_stat = True
        #self.live_span = ...
        self.user_id = g.user.id

    def __repr__(self):
        return '<Course %r>' % self.title


class Meeting(db.Model):
    __searchable__ = ['title','note','kwd1', 'kwd2', 'kwd3', 'kwd4','kwd5']

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    demo_email = db.Column(db.String, db.ForeignKey('demo.email', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(140))  #a tweet length
    type_meeting = db.Column(db.Integer) #0: class, 1: seminar 2: meeting
    close_stat = db.Column(db.Integer) #0: open (getting feedback), 1: closed (comments still visible) 2: closed (comments no longer visible)
    close_opt = db.Column(db.Integer) #once closed, 1: comments still visible, and 2: closed with comments no longer visible. default 2, can be set from user setting
    timestamp = db.Column(db.DateTime)
    url_string = db.Column(db.String(80))  #auto-generated: 64-character?
    prompt = db.Column(db.String(100))
    live_till =  db.Column(db.DateTime) #0: default same as the classes
    live_till_hours = db.Column(db.Integer) # default could be 14 days = 14*24 hours
    note = db.Column(db.String(500))
    muddies = db.relationship('Muddy', backref='meeting', lazy='dynamic', cascade="all, delete-orphan")
    kwd1 =  db.Column(db.String(100))  #think of making this into disciplines/sub-dis
    kwd2 =  db.Column(db.String(100))
    kwd3 =  db.Column(db.String(100))
    kwd4 =  db.Column(db.String(100))
    kwd5 =  db.Column(db.String(100))


    #@staticmethod
    #def make_url():
        #url = str(g.meeting.id)+''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(64))
        #return url


    def __init__(self,title,course_id,prompt,close_opt,live_till_hours):
        self.title = title
        self.course_id = course_id  # Or should it be just course.id instead of g.course.id?
        #self.url_string
        self.prompt = prompt
        self.url_string = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(64))
        self.timestamp = datetime.utcnow()
        self.close_opt = close_opt
        self.live_till = self.timestamp + timedelta(hours = live_till_hours)
        #self.live_span = ...

    def __repr__(self):
        return '<Meetings %r>' % self.title

class Muddy(db.Model):
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(700))  #5 tweets length
    like_count = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    demo_email = db.Column(db.String, db.ForeignKey('demo.email', ondelete='CASCADE'), nullable=False)

    def __init__(self,body,meeting_id,like_count):
        self.body = body
        self.timestamp = datetime.utcnow()
        self.meeting_id = meeting_id
        self.like_count = like_count# Or should it be just meeting.id instead of g.course.id?

    def __repr__(self):
        return '<Muddy %r>' % self.body

if enable_search:
    #whooshalchemy.whoosh_index(app, User)
    whooshalchemy.whoosh_index(app, Course)
    whooshalchemy.whoosh_index(app, Meeting)
    whooshalchemy.whoosh_index(app, Muddy)
'''
if enable_search:
    whooshalchemy.whoosh_index(app, Course)
'''

class Demo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, nullable=False, unique=True)
    all_meetings = db.relationship('Meeting', backref='demo', lazy='dynamic', cascade="all, delete-orphan")
    all_muddies = db.relationship('Muddy', backref='demo', lazy='dynamic', cascade="all, delete-orphan")

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<Demo %r>' % (self.email)

    def __init__(self,email):
        self.email = email


class Wantbeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(140), index=True, nullable=False, unique=True)
    #get region/browser/OS later?

    def __init__(self,email):
        self.email = email
