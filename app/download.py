from flask import render_template
from flask_mail import Message
from app import mail
from .decorators import async
from config import ADMINS, DOWNLOAD_FOLDER, SITE
from datetime import datetime
from app import app

def file_desc(reguser):
    dt = datetime.utcnow()
    t_string = dt.strftime('%Y-%m-%d-%H-%M-%S')
    filename = 'fc_'+reguser.email+'_'+t_string+'_.csv'
    file_out = DOWNLOAD_FOLDER+filename

    return(t_string,filename,file_out)

def legends(file_out,dt):
    with open(file_out,'a+') as file:
        file.write('"\n\n#BR" represents the total number of "nothing to add" responses on the feedback form.\n')
        file.write('"#Likes" represents the total number of upvotes a comment received.\n')
        file.write('"#FB" represents the total number of comments a form received.\n')
        file.write('Report generated at '+dt+' (UTC)\n')

def muddy_info(file_out, meet):
    with open(file_out,'a+') as file:
        if meet.muddies.count() == 0:
            file.write('No comments available for form {}\n\n\n'.format(meet.title))
            return
        else:
            file.write('DETAILS OF FEEDBACK COMMENTS FOR FORM:,{}\n'.format(meet.title))
            file.write('#Likes, Timestamp (UTC), Comment\n')
            for muddy in meet.muddies:
                file.write('{},{},{}\n'.format(muddy.like_count, muddy.timestamp, muddy.body))
            return    
                
def meet_info(file_out, meet):
    with open(file_out,'a+') as file:
        file.write('\nForm title:, {}\n'.format(meet.title))
        file.write('Prompt:, {}\n'.format(meet.prompt))
        file.write('Timestamp (UTC):, {}\n'.format(meet.timestamp))
        file.write('Note:, {}\n'.format(meet.note))
        file.write('URL:, '+SITE+'/m/{}\n'.format(meet.url_string))
        file.write('#FB:, {}\n'.format(meet.muddies.count()))
        file.write('#BR:, {}\n'.format(meet.blank_response))
        if (meet.close_stat > 0):
            file.write('Accepting feedback?, No\n\n')
        else:
            file.write('Accepting feedback?, Yes\n\n')

    return


def course_dl(reguser,course):
    print reguser.email, course.title

    t_string,filename,file_out = file_desc(reguser)
    
    with open(file_out,'a+') as file:
        file.write('DETAILS OF FORMS CONTAINED IN FOLDER:, {}\n\n\n\n'.format(course.title))

    for meet in course.meetings:
        meet_info(file_out, meet)
        muddy_info(file_out, meet)
    legends(file_out,t_string)
        
    return(filename)


def meeting_dl(reguser,meet):
    print reguser.email, meet.title

    t_string,filename,file_out = file_desc(reguser)
    
    with open(file_out,'a+') as file:
        file.write('DETAILS OF FORM:, {}\n\n\n\n'.format(meet.title))

    meet_info(file_out, meet)
    muddy_info(file_out, meet)
    legends(file_out,t_string)
        
    return(filename)
