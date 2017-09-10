from flask import render_template
from flask_mail import Message
from app import mail
from .decorators import async
from config import ADMINS, DOWNLOAD_FOLDER
from app import app


def prep_dl(reguser,course):
    print reguser.email, course.title
    #print 'Hi {}, this is the course content for {}'.format(reguser.nickname, course.title)
    with open(DOWNLOAD_FOLDER+'cc_'+reguser.nickname+'_'+course.title+'.csv','w+') as file:
        file.write('Hello there!,{}, Course {}'.format(reguser.email,course.title))

    filename = 'cc_'+reguser.nickname+'_'+course.title+'.csv'
    return(filename)
