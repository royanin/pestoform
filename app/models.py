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

meeting_emails = db.Table('meeting_emails',
        db.Column('meeting_id', db.Integer, db.ForeignKey('meeting.id')),
        db.Column('email_id', db.Integer, db.ForeignKey('email.id')))

    
roles_users = db.Table('roles_users',
        db.Column('reguser_id', db.Integer(), db.ForeignKey('reguser.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class Reguser(db.Model, UserMixin):
    #__tablename__ = 'regusers'
    id = db.Column(db.Integer, primary_key=True)
    #social_id = db.Column(db.String(64), nullable=False, unique=True)
    social_nw = db.Column(db.String(64))
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(100), index=True, nullable=True, unique=True)
    password = db.Column(db.String(255), nullable=True)
    courses = db.relationship('Course', backref='reguser',lazy='dynamic', cascade="all, delete-orphan")
    all_meetings = db.relationship('Meeting', backref='reguser', lazy='dynamic', cascade="all, delete-orphan")
    all_muddies = db.relationship('Muddy', backref='reguser', lazy='dynamic', cascade="all, delete-orphan")
    active = db.Column(db.Boolean())
    last_seen = db.Column(db.DateTime)
    affiliation = db.Column(db.String(100))
    roles = db.relationship('Role', secondary=roles_users,backref=db.backref('regusers', lazy='dynamic'))
    confirmed_at = db.Column(db.DateTime)
    

    
    @staticmethod
    def make_unique_nickname(nickname):
        if Reguser.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if Reguser.query.filter_by(nickname=new_nickname).first() is None:
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


    def __repr__(self):
        return '<Reguser %r>' % (self.nickname)

class Course(db.Model):
    __searchable__ = ['title','sbj1', 'sbj2', 'sbj3']

    id = db.Column(db.Integer, primary_key=True)
    title =  db.Column(db.String(100))
    type_course = db.Column(db.Integer) #0: traditional course, 1: seminar 2: event 3: workshop etc.
    level =  db.Column(db.Integer)   #0: none, 1-3: K-12, 4-UGL 5-UGU 6-grad, 7-LLL, 8-Service Learning 
    sbj1 =  db.Column(db.String(100))  #think of making this into disciplines/sub-dis
    sbj2 =  db.Column(db.String(100))
    sbj3 =  db.Column(db.String(100))
    timestamp = db.Column(db.DateTime)
    #live_till =  db.Column(db.DateTime) #0: datetime- 6-months -- the course will be archived after that, 1: never, 2: now 3: 1 week, 4: 3-months, 5: year
    live_stat = db.Column(db.Boolean) #True:live, False:archived
    #del_stat = db.Column(db.Boolean) 
    reguser_id = db.Column(db.Integer, db.ForeignKey('reguser.id', ondelete='CASCADE'), nullable=False)
    meetings = db.relationship('Meeting', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    note = db.Column(db.String(500))

    def __init__(self,title,level):
        self.title = title
        self.timestamp = datetime.utcnow()
        self.live_stat = True
        #self.live_span = ...
        self.reguser_id = g.reguser.id

    def __repr__(self):
        return '<Course %r>' % self.title


class Meeting(db.Model):
    __searchable__ = ['title','note','prompt']

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'), nullable=False)
    reguser_id = db.Column(db.Integer, db.ForeignKey('reguser.id', ondelete='CASCADE'), nullable=False)
    #demo_email = db.Column(db.String(100), db.ForeignKey('demo.email', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(100))  #a tweet length
    type_meeting = db.Column(db.Integer) #0: class, 1: seminar 2: meeting
    close_stat = db.Column(db.Integer) #0: open (getting feedback), 1: closed (comments still visible) 2: closed (comments no longer visible)
    close_opt = db.Column(db.Integer) #once closed, 1: comments still visible, and 2: closed with comments no longer visible. default 2, can be set from user setting
    timestamp = db.Column(db.DateTime)
    url_string = db.Column(db.String(80))  #auto-generated: 64-character?
    prompt = db.Column(db.String(300))
    live_till =  db.Column(db.DateTime) #0: default same as the classes
    live_till_hours = db.Column(db.Integer) # default could be 14 days = 14*24 hours
    note = db.Column(db.String(500))
    muddies = db.relationship('Muddy', backref='meeting', lazy='dynamic', cascade="all, delete-orphan")
    blank_response = db.Column(db.Integer)
    emails = db.relationship("EmailList", secondary=meeting_emails, backref=db.backref('meetings', lazy='dynamic'))

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
    reguser_id = db.Column(db.Integer, db.ForeignKey('reguser.id', ondelete='CASCADE'), nullable=False)
    #demo_email = db.Column(db.String(100), db.ForeignKey('demo.email', ondelete='CASCADE'), nullable=False)

    def __init__(self,body,meeting_id,like_count):
        self.body = body
        self.timestamp = datetime.utcnow()
        self.meeting_id = meeting_id
        self.like_count = like_count# Or should it be just meeting.id instead of g.course.id?

    def __repr__(self):
        return '<Muddy %r>' % self.body


class EmailList(db.Model):
    __tablename__ = 'email'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), index=True, nullable=False, unique=True)


    def __init__(self,email):
        self.email = email

    def __repr__(self):
        return '<Email %r>' % self.email
    
if enable_search:
    whooshalchemy.whoosh_index(app, Course)
    whooshalchemy.whoosh_index(app, Meeting)
    whooshalchemy.whoosh_index(app, Muddy)
