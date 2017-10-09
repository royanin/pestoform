from flask import render_template
from flask_mail import Message
from app import mail
from .decorators import async
from config import ADMINS,URGENT_EMAIL
from app import app
from smtplib import SMTPException


@async
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)    
        except SMTPException,e:
            #return str("Please enter a valid email id")
            return str(e)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)

def course_view(reguser,course):
    print 'Hi, this is emails.py course_view'
    send_email(#"Hi %s !" % reguser.email,
               "Pestoform: requested stuff",
               ADMINS[0],
               [reguser.email],
               render_template("email_course_view.txt",
                               reguser=reguser, course=course),
               render_template("email_course_view.html",
                               reguser=reguser, course=course))

def meeting_view(reguser,meeting):
    print 'Hi, this is emails.py meeting_view'
    send_email(#"Hi %s !" % reguser.email,
               "Pestoform: requested stuff",
               ADMINS[0],
               [reguser.email],
               render_template("email_meeting_view.txt",
                               reguser=reguser, meeting=meeting),
               render_template("email_meeting_view.html",
                               reguser=reguser, meeting=meeting))


def form_open(email,meeting):
    print 'Hi, this is emails.py form_open'
    send_email(#"Hi %s!" % email,
               "Hello from Pestoform!",
               ADMINS[0],
               [email],
               render_template("email_form_open.txt",
                               email=email, meeting=meeting),
               render_template("email_form_open.html",
                               email=email, meeting=meeting))

def form_share_email(list_to, request_from, meeting):
    print 'Hi, this is emails.py form_share_email'
    send_email("Feedback request: From %s"% request_from,
               #"Hello from Pestoform!",
               ADMINS[0],
               list_to,
               render_template("email_form_share.txt",
                               email=request_from, meeting=meeting),
               render_template("email_form_share.html",
                               email=request_from, meeting=meeting))

    
def eoi_noted(email):
    print 'Hi, this is emails.py sending eoi noted email'
    send_email(#"Hi %s!" % email,
               "Hello from Pestoform!",
               ADMINS[0],
               [email],
               render_template("email_eoi.txt",
                               email=email),
               render_template("email_eoi.html",
                               email=email))


def notify_server_error():
    print URGENT_EMAIL
    send_email(#"Hi %s!" % email,
               "Pestoform Failure!(URGENT)",
               ADMINS[0],
               [URGENT_EMAIL],
               render_template("email_server_fail.txt",
                               email=URGENT_EMAIL),
               render_template("email_server_fail.html",
                               email=URGENT_EMAIL))
