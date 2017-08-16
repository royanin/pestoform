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

class Demo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, nullable=False, unique=True)
    all_meetings = db.relationship('Meeting_demo', backref='demo', lazy='dynamic', cascade="all, delete-orphan")
    all_muddiess = db.relationship('Muddy_demo', backref='demo', lazy='dynamic', cascade="all, delete-orphan")
            
    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<Demo %r>' % (self.email)

class Meeting_demo(db.Model):
    __searchable__ = ['title']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))  #a tweet length
    type_meeting = db.Column(db.Integer) #0: class, 1: seminar 2: meeting
    close_stat = db.Column(db.Integer) #0: open (getting feedback), 1: closed (comments still visible) 2: closed (comments no longer visible)
    close_opt = db.Column(db.Integer) #once closed, 1: comments still visible, and 2: closed with comments no longer visible. default 2, can be set from user setting
    timestamp = db.Column(db.DateTime)
    url_string = db.Column(db.String(80))  #auto-generated: 64-character?
    prompt = db.Column(db.String(100))
    live_till =  db.Column(db.DateTime) #0: default same as the classes
    live_till_hours = db.Column(db.Integer) # default could be 14 days = 14*24 hours
    demo_email = db.Column(db.Integer, db.ForeignKey('demo.email', ondelete='CASCADE'), nullable=False)
    muddies_demo = db.relationship('Muddy_demo', backref='meeting_demo', lazy='dynamic', cascade="all, delete-orphan")
    

    def __init__(self,title,prompt, close_opt,live_till_hours, demo_email):
        self.title = title
        self.prompt = prompt
        self.url_string = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(64))
        self.timestamp = datetime.utcnow()
        self.demo_email = demo_email
        self.close_opt = close_opt
        self.live_till = self.timestamp + timedelta(hours = live_till_hours)
        
    def __repr__(self):
        return '<Meeting_demo %r>' % self.title

class Muddy_demo(db.Model):
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(700))  #5 tweets length
    like_count = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    meeting_demo_id = db.Column(db.Integer, db.ForeignKey('meeting_demo.id', ondelete='CASCADE'), nullable=False)
    demo_email = db.Column(db.Integer, db.ForeignKey('demo.email', ondelete='CASCADE'), nullable=False)

    def __init__(self,body,meeting_demo_id, demo_email, like_count):
        self.body = body
        self.timestamp = datetime.utcnow()
        self.meeting_demo_id = meeting_demo_id
        self.demo_email = meeting_demo_id.demo_email
        self.like_count = like_count# Or should it be just meeting.id instead of g.course.id?

    def __repr__(self):
        return '<Muddy_demo %r>' % self.body

if enable_search:
    whooshalchemy.whoosh_index(app, Meeting_demo)
    whooshalchemy.whoosh_index(app, Muddy_demo)
