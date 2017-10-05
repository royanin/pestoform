from flask import render_template, flash, redirect, session, url_for, request, g, json, jsonify, send_from_directory
from flask_security import login_user, logout_user, current_user, login_required
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
#from flask_login import login_user, logout_user, current_user, login_required, UserMixin, RoleMixin
from datetime import datetime,timedelta
from dateutil import parser
import pytz
from app import app, db, lm #, oid
from .forms import LoginForm, EditForm, CourseForm, MeetingForm, SearchForm, ChangeIndexForm, MuddyForm, DemoForm, WantbetaForm, GenForm
from .models import Role, Reguser, Course, Meeting, Muddy, Demo, Wantbeta
#from .emails import follower_notification
from config import COURSES_PER_PAGE, MEETINGS_PER_PAGE, FEEDBACK_PER_PAGE, MAX_SEARCH_RESULTS, OAUTH_CREDENTIALS,GOOGLE_CLIENT_ID, SORTING_TYPE
from .emails import course_view, meeting_view, form_open, eoi_noted, notify_server_error, form_share_email
from .download import course_dl, meeting_dl
from oauth import OAuthSignIn
from oauth2client import client, crypt
from apiclient import discovery
import httplib2, re
from validate_email import validate_email
from sqlalchemy import desc, func, select
#from flask.ext.social import Social
#from flask.ext.social.datastore import SQLAlchemyConnectionDatastore

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, Reguser, Role)
#connection_datastore = SQLAlchemyConnectionDatastore(db, Connection)
security = Security(app, user_datastore)
#social = Social(app, connection_datastore) 

@lm.user_loader
def load_user(id):
    return Reguser.query.get(int(id))
    

 
@app.before_request
def before_request():
    g.reguser = current_user
    g.muddy_form = MuddyForm()
    g.demo_form = DemoForm()
    g.wantbeta_form = WantbetaForm()
    g.gen_form =  GenForm()
    g.GOOGLE_CLIENT_ID = GOOGLE_CLIENT_ID
    if g.reguser.is_authenticated:
        g.reguser.last_seen = datetime.utcnow()
        db.session.add(g.reguser)
        db.session.commit()
        g.search_form = SearchForm()
        g.course_form = CourseForm()
        g.meeting_form = MeetingForm()
        g.change_index_form = ChangeIndexForm()
       

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    notify_server_error()
    return render_template('500.html'), 500

##Social login using Miguel oauth begins

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    
    social_id, username, email = oauth.callback()
    if social_id is None or email is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    reguser = Reguser.query.filter_by(email=email).first()

    if not reguser:
        nickname = Reguser.make_unique_nickname(email.split('@')[0])
        reguser = Reguser(password="something_complicated", nickname=nickname, email=email)
        db.session.add(reguser)
        db.session.commit()
    login_user(reguser, True)
    return redirect(url_for('index'))

##Social login using Miguel oauth ends

##########trying google signin BEGINS



##########trying google signin ENDS

        
@app.route('/gcallback',methods = ['GET','POST'])
def gcallback_request():
    
    token = request.form['id_token']
    print '\n\n token:',token
    try:
        idinfo = client.verify_id_token(token, GOOGLE_CLIENT_ID)
        print '\n\n\n in google auth'

        # Or, if multiple clients access the backend server:
        #idinfo = client.verify_id_token(token, None)
        #if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #    raise crypt.AppIdentityError("Unrecognized client.")

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")

        else:
            print idinfo['email'], idinfo['name']
            email = idinfo['email']

            reguser = Reguser.query.filter_by(email=email).first()

            if not reguser:
                nickname = Reguser.make_unique_nickname(email.split('@')[0])
                reguser = Reguser(password="something_complicated", nickname=nickname, email=email, social_nw = 'google')
                db.session.add(reguser)
                db.session.commit()
            login_user(reguser, True)
            print '\n\nam I logged in?'
            return redirect(url_for('index'))
        
        # If auth request is from a G Suite domain:
        #if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #    raise crypt.AppIdentityError("Wrong hosted domain.")
    except crypt.AppIdentityError:
        # Invalid token
        reguserid = idinfo['sub']

    
    #return redirect(url_for('index'))
    return redirect(url_for('index'))

#@app.route('/', methods=['GET', 'POST'])
#@app.route('/index', methods=['GET', 'POST'])
#@app.route('/view_folder', methods=['GET', 'POST'])
@app.route('/add_course_session', methods=['GET', 'POST'])
@login_required
def add_course_session():
    results = request.form.getlist('id')
    #print 'results',results
    #print session
    if len(results) > 0:
        course = Course.query.get(int(results[0]))
        #print course.id, course.title
        session['course_num'] = course.id
        session['course_title'] = course.title
    #return None
    return redirect(url_for('index')+'#new_meeting_link')
    

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    
    if g.reguser.is_authenticated:
        print '\n\n\nrequest headers:',request.headers.get('User-Agent')
        print '\n\n\nrequest headers:',request.remote_addr
        print '\n\n\nrequest headers:',request.environ['REMOTE_ADDR']
        
        g.reguser.last_seen = datetime.utcnow()
        if g.reguser.nickname is None or g.reguser.nickname == "":
            g.reguser.nickname = Reguser.make_unique_nickname(g.reguser.email.split('@')[0])
        #print 'Here in index page'
            print g.reguser.nickname
            db.session.add(g.reguser)
            db.session.commit()

        if g.reguser.courses.count() == 0:
            course = Course(title="Uncategorized",level=0)
            db.session.add(course)
            db.session.commit()
            session['course_num'] = course.id
            session['course_title'] = course.title
            print session['course_num'],session['course_title']
            #print 'initial courses:', None
        else:
            print 'courses exist'          
        
        
    if 'course_num' in session:
        course_id = session['course_num']
    
    else:
        session['course_num'] = 0
        course_id = session['course_num']
        
    print 'In index view: course_id:',course_id
    live_courses = g.reguser.courses.filter_by(live_stat=True)
    course = Course.query.get(course_id)
    live_num = g.reguser.courses.filter_by(live_stat=True).count()
    archived_num = g.reguser.courses.filter_by(live_stat=False).count()
        
    if (course):
        session['course_title'] = course.title
        meetings = course.meetings.paginate(page, MEETINGS_PER_PAGE, False)
        #meetings = course.meetings.filter_by(id)
    else:
        meetings = []
    
    return render_template('index.html',
                           title='Home',
                           reguser = g.reguser,
                           #form=g.course_form,
                           live_courses=live_courses,
                           live_num=live_num,
                           archived_num=archived_num,
                           #meetings_sorted=meetings_sorted,
                           courses=g.reguser.courses,
                           #course_id = course_id
                           meetings=meetings,
                           timenow=datetime.now(),
                           GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID)


##########################
@app.route('/', methods=['GET', 'POST'])
@app.route('/view', methods=['GET', 'POST'])
@app.route('/view/<int:page>', methods=['GET', 'POST'])
@login_required
def view(page=1):
    
    if g.reguser.is_authenticated:
        g.reguser.last_seen = datetime.utcnow()
        if g.reguser.nickname is None or g.reguser.nickname == "":
            g.reguser.nickname = Reguser.make_unique_nickname(g.reguser.email.split('@')[0])
        #print 'Here in index page'
            print g.reguser.nickname
            db.session.add(g.reguser)
            db.session.commit()
        print '\n\n\n user details:',g.reguser.nickname,g.reguser.email,g.reguser.password, g.reguser.social_nw
        print '\n\nsession:',session

        
    if 'course_num' in session:
        course_id = session['course_num']
    
    else:
        session['course_num'] = 0
        course_id = session['course_num']
        
    print 'In index view: course_id:',course_id
    live_courses = g.reguser.courses.filter_by(live_stat=True)
    course = Course.query.get(course_id)

    print request.form.get('sorting_id')
    try:
        sorting_id = int(request.form.get('sorting_id'))
        session['sorting_id'] = sorting_id
        session['sorting_type'] = SORTING_TYPE[session['sorting_id']]
        print 'sorint_id from form submission: ',sorting_id 
    except TypeError:
        sorting_id = 0
        session['sorting_id'] = sorting_id
        session['sorting_type'] = SORTING_TYPE[session['sorting_id']]
    print sorting_id
    #if sorting_id is None:
        #sorting_id = 1
    if sorting_id == 0:
        print 'In sorting_id 0'
        meetings_sorted = Meeting.query.filter_by(reguser_id=g.reguser.id).order_by(desc(Meeting.timestamp))
    elif sorting_id == 1:
        print 'In sorting_id 1'
        meetings_sorted = Meeting.query.filter_by(reguser_id=g.reguser.id).order_by(Meeting.timestamp)
    elif sorting_id == 2:
        meetings_sorted = Meeting.query.filter_by(reguser_id=g.reguser.id).order_by(Meeting.course_id)
    elif sorting_id == 3:
        meetings_sorted = Meeting.query.filter_by(reguser_id=g.reguser.id).order_by(desc(Meeting.course_id))
    elif sorting_id == 4:
        stmt = db.session.query(Muddy.meeting_id, func.count('*').label('muddy_count')).group_by(Muddy.meeting_id).subquery()
        #meetings_sorted = db.session.query(Meeting).filter(Meeting.reguser_id==g.reguser.id).outerjoin((stmt,Meeting.id==stmt.c.meeting_id)).order_by(stmt.c.muddy_count.desc())
        meetings_sorted = Meeting.query.filter(Meeting.reguser_id==g.reguser.id).outerjoin((stmt,Meeting.id==stmt.c.meeting_id)).order_by(stmt.c.muddy_count.desc())
    elif sorting_id == 5:
        stmt = db.session.query(Muddy.meeting_id, func.count('*').label('muddy_count')).group_by(Muddy.meeting_id).subquery()
        #meetings_sorted = db.session.query(Meeting).filter(Meeting.reguser_id==g.reguser.id).outerjoin((stmt,Meeting.id==stmt.c.meeting_id)).order_by(stmt.c.muddy_count)
        meetings_sorted = Meeting.query.filter(Meeting.reguser_id==g.reguser.id).outerjoin((stmt,Meeting.id==stmt.c.meeting_id)).order_by(stmt.c.muddy_count)    
        
    for meet in meetings_sorted:
        print meet.id, meet.reguser_id, meet.title, meet.timestamp, meet.muddies.count()

    live_num = g.reguser.courses.filter_by(live_stat=True).count()
    archived_num = g.reguser.courses.filter_by(live_stat=False).count()

        
    if (course):
        session['course_title'] = course.title
        meetings = course.meetings.paginate(page, MEETINGS_PER_PAGE, False)
        #meetings = course.meetings.filter_by(id)
    else:
        meetings = []
    
    meetings_sorted = meetings_sorted.paginate(page, MEETINGS_PER_PAGE, False)
    

    #for meeting in meetings_sorted:
        #print meeting, meetings_sorted.has_prev
    
    session['bc_type'] = None
    session['bc_page'] = None
    session['bc_url'] = None
    return render_template('view.html',
                           title='Home',
                           reguser = g.reguser,
                           #form=g.course_form,
                           live_courses=live_courses,
                           live_num=live_num,
                           archived_num=archived_num,
                           meetings_sorted=meetings_sorted,
                           courses=g.reguser.courses,
                           #course_id = course_id
                           meetings=meetings,
                           SORTING_TYPE=SORTING_TYPE,
                           len_SORTING_TYPE = len(SORTING_TYPE))

##########################

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/view_folder', methods=['GET', 'POST'])
@app.route('/view_folder/<int:page>', methods=['GET', 'POST'])
@login_required
def view_folder(page=1):
    try:
        course_id = int(request.form.get('course_id'))
    except TypeError:
        course_id = session['course_num']
        #course.title = session['course_title']
    reguser = g.reguser
    course = Course.query.get(course_id)

    session['course_num'] = course.id
    session['course_title'] = course.title
        
    course_meetings = course.meetings.paginate(page, MEETINGS_PER_PAGE, False)
    session['bc_type'] = 'fo'
    session['bc_page'] = str(page)
    session['bc_url'] = None

    
    print "In view folder:",course.title
    return render_template('view_folder.html',
                           #live_num = live_num,
                           #archived_num = archived_num,
                           reguser=reguser,
                           courses=reguser.courses,
                           course=course,
                           course_meetings=course_meetings)
    


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@app.route('/course_action_edit', methods=['GET','POST'])
@login_required
def course_action_edit():
    g.course_form = CourseForm()
    print 'title: ', g.course_form.title.data
    print 'level: ', g.course_form.level.data
    g.course_form.level.data = 2
    print 'level: ', g.course_form.level.data
    #if request.method == "POST":
        #print 'req met = post'
    #if g.course_form.validate_on_submit():
        #print 'form validated on submit'
    if request.method == "POST" and g.course_form.validate_on_submit():
        print 'In course_create view2'
    #if g.course_form.validate_on_submit():
        id = g.course_form.id.data
        if (id):
            course = Course.query.get(id)
            course.title = g.course_form.title.data
            course.level = g.course_form.level.data
            #course.body = g.course_form.body.data
        else:
            course = Course(g.course_form.title.data, g.course_form.level.data)
        db.session.add(course)
        db.session.commit()
        session['course_num'] = course.id
        session['course_title'] = course.title
        flash('{} has been created!'.format(course.title))
    return redirect(url_for('index'))
    #return redirect(url_for('index')+'#id-'+str(course.id))
    #return render_template('index.html',
                           #title='Home',
                           #form=g.course_form,
                           #courses=courses)


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@app.route('/course_archive', methods=['GET', 'POST'])
@login_required
def course_archive():
    print 'Here in course_archive!'
    results = request.form.getlist('id')
    print 'results:',results
    for item in results:
        print 'item:',item
        if (item):
            course = Course.query.get(int(item))
            print 'course is:',int(item), course
            if course.live_stat==True:
                course.live_stat = False
                flash('{} is now archived.'.format(course.title))
            else:
                course.live_stat = True
                flash('{} is now live.'.format(course.title))
            #db.session.delete(course)
            db.session.commit()
            session['course_num'] = course.id
            session['course_title'] = course.title
            return redirect(url_for('view_folder'))

        

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@app.route('/course_delete', methods=['GET', 'POST'])
@login_required
def course_delete():
    print 'Here in course_delete!'
    results = request.form.getlist('id')
    print 'results:',results
    for item in results:
        print 'item:',item
        if (item):
            course = Course.query.get(int(item))
            print 'course is:',int(item), course
            db.session.delete(course)
            db.session.commit()
            course_uncat = Course.query.filter_by(reguser_id=g.reguser.id).filter_by(title="Uncategorized").first()
            #print course_uncat.id, course_uncat.title
            session['course_num'] =  course_uncat.id
            session['course_title'] = course_uncat.title

            flash('{} has been deleted!'.format(course.title))
            return redirect(url_for('view'))

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/view', methods=['GET', 'POST'])
@app.route('/view/<int:page>', methods=['GET', 'POST'])
@app.route('/meeting_note', methods=['GET', 'POST'])
@login_required
def meeting_note():
    g.meeting_form = MeetingForm()
    print 'Here in meeting_note!'
    results = request.form.getlist('meeting_id')
    
    print 'results:',results
    if request.method == "POST" and g.meeting_form.validate_on_submit():
        meeting = Meeting.query.get(int(results[0]))
        meeting.note = g.meeting_form.note.data
 
        print 'meeting note is:', meeting.note
             
        db.session.commit()
        return ('', 204)
 
        
@app.route('/meeting_close', methods=['GET', 'POST'])
@login_required
def meeting_close():
    print 'Here in meeting_close!'

    results = request.form.getlist('meeting_id')   
    results2 = request.form['closeopt']
    print 'results:',results, results2
    
    if request.method == "POST" and g.meeting_form.validate_on_submit():
    #for item in results:
        print 'validated'
        meeting_id = int(results[0])
        print 'meeting_id', int(results[0])

        meeting = Meeting.query.get(meeting_id)
        print meeting, meeting.id, meeting.close_stat

        meeting.close_stat = int(results2)
        db.session.commit()
        print 'meeting live till:', meeting.live_till
        print 'meeting is:',id, meeting
        if meeting.close_stat == 0 and (meeting.live_till < datetime.utcnow()):
            meeting.live_till = datetime.utcnow() + timedelta(hours = 14*24)
            db.session.commit()
            print 'meeting live till:', meeting.live_till
            flash('{} (under {}) is now open. If you want to change this duration, please go to the "edit form details" menu under form options.'.format(meeting.title, meeting.course.title))
        elif meeting.close_stat == 1:
            flash('{} (under {}) NOT receiving feedback; old comments still visible'.format(meeting.title, meeting.course.title))
        elif meeting.close_stat == 2:
            flash('{} (under {}) NOT receiving feedback; old comments hidden'.format(meeting.title, meeting.course.title))

    return ('', 204)

 
@app.route('/meeting_delete', methods=['GET', 'POST'])
@login_required
def meeting_delete():
    print 'Here in meeting_delete!'
    results = request.form.getlist('id')
    print 'results:',results
    for item in results:
        print 'item:',item
        if (item):
            meeting = Meeting.query.get(int(item))
            print 'meeting is:',int(item), meeting
            flash('{} (under {}) has been deleted!'.format(meeting.title, meeting.course.title))
            db.session.delete(meeting)
            db.session.commit()
            return redirect(url_for('view'))

@app.route('/new_meeting', methods=['GET','POST'])
@login_required
def new_meeting():
    print 'Here in new meeting!'
    return redirect(url_for('index')+'#new_meeting_link')
    #return render_template('link_new_meeting.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/stuff', methods=['GET','POST'])
#@login_required
def stuff():
    print 'Here in stuff!'
    return render_template('stuff.html')
    #return redirect(url_for('stuff.html'))
    #return redirect(url_for('stuff.html'))

'''
@app.route('/new_course', methods=['GET','POST'])
@login_required
def new_course():
    print 'Here in new course!'
    return redirect(url_for('index'))
    #return render_template('link_new_course.html')
'''
@app.route('/meeting_action_edit', methods=['GET','POST'])
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def meeting_action_edit():
    g.meeting_form = MeetingForm()
    print 'In meeting form:\n',request, request.method
    if request.method == "POST" and g.meeting_form.validate_on_submit():
    #print '\n\n',g.meeting_form.errors
        id = g.meeting_form.id.data        
        
        print 'meeting id is:',id
        if (id):
            #for item in request.data:
            print request.data
            print '\n\n\nHere in meeting',id
            meeting = Meeting.query.get(id)
            
            lt_info = request.form.get('live_till')
            dt = parser.parse(lt_info)
            dso = dt.astimezone(pytz.timezone('UTC'))

            meeting.title = g.meeting_form.title.data
            meeting.prompt = g.meeting_form.prompt.data
            meeting.course_id = g.meeting_form.course_id.data
            meeting.close_opt = g.meeting_form.close_opt.data
            meeting.live_till = datetime(dso.year,dso.month,dso.day,dso.hour,dso.minute)
            
            db.session.commit()
            return ('', 204)

        else:
            print "from meeting forms:", g.meeting_form.title.data,g.meeting_form.course_id.data,g.meeting_form.prompt.data,g.meeting_form.close_opt.data,g.meeting_form.live_till_month.data, g.meeting_form.live_till_days.data, g.meeting_form.live_till_hours.data
            meeting = Meeting(g.meeting_form.title.data,g.meeting_form.course_id.data,g.meeting_form.prompt.data,g.meeting_form.close_opt.data,30*24*int(g.meeting_form.live_till_month.data) + 24*int(g.meeting_form.live_till_days.data) + int(g.meeting_form.live_till_hours.data))
            meeting.close_stat = 0
            meeting.reguser_id = g.reguser.id
            meeting.demo_email = "NA"
            meeting.blank_response = 0
            session['course_num'] = meeting.course_id
            
            db.session.add(meeting)
            db.session.commit()
            #flash('{} (under {}) has been created!'.format(meeting.title, meeting.course.title))
            #print "Meeting",meeting.title,"under",meeting.course.title,"with prompt:",meeting.prompt,"has been created"
        
            #return redirect(url_for('index'))
            #return redirect(url_for('index')+'#id-'+str(meeting.course.id))
            return render_template(('new_form_details.html'),
                           meeting=meeting)


@app.route('/', methods=['GET', 'POST'])
@app.route('/view', methods=['GET', 'POST'])
@app.route('/view/<int:page>', methods=['GET', 'POST'])
@app.route('/view_feedback/<url_string>', methods=['GET', 'POST'])
@app.route('/view_feedback/<url_string>/<int:page>', methods=['GET', 'POST'])
def view_feedback(url_string,page=1):
    print '\n\n\nin m: url_string:',url_string
    #
    meeting = Meeting.query.filter_by(url_string=url_string).first()
    #print 'meeting.id:, request.method',meeting.id, request.method
    #muddy = None 

    if  meeting is None:
        #return redirect(url_for('index'))
        return redirect(url_for('view'))

    else:
        meeting_id = meeting.id
        muddies = Muddy.query.filter_by(meeting_id=meeting.id).order_by(desc(Muddy.like_count))
        muddies_total = muddies.count()
        print '\n\n\n m_total:',muddies_total
        meeting_muddies = muddies.paginate(page, FEEDBACK_PER_PAGE, False)
        #for muddy in meeting_muddies:
            #print muddy.body
        #paginate the muddies sent back?
        #print 'muddy id:',g.muddy_form.id.data
        session['url_string'] = url_string
        session['course_num'] = meeting.course_id
        session['course_title'] = meeting.course.title
        session['bc_type'] = 'fi'
        session['bc_page'] = str(page)
        session['bc_url'] = url_string
        
        return render_template(('view_feedback.html'),
                           url_string=url_string,
                           meeting=meeting,
                           meeting_muddies=meeting_muddies,
                           muddies_total=muddies_total)
                           #g.muddy_form = MuddyForm())

@app.route('/m/<url_string>', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
#@app.route('/index/<int:page>', methods=['GET', 'POST'])
def m(url_string):
    print '\n\n\nin m: url_string:',url_string
    #
    meeting = Meeting.query.filter_by(url_string=url_string).first()
    #print 'meeting.id:, request.method',meeting.id, request.method
    muddy = None 

    if  meeting == None:
        return render_template('form_not_found.html')


    else:
        meeting_id = meeting.id
        muddies = meeting.muddies
        #print 'muddy id:',g.muddy_form.id.data
        session['url_string'] = url_string

        #Determine close_stat based on live_till:
        if datetime.utcnow() > meeting.live_till:
            print 'meeting live_till',meeting.live_till
            print 'time now:', datetime.utcnow()
            print 'meeting.close_stat, meeting.close_opt:', meeting.close_stat,meeting.close_opt
            meeting.close_stat = meeting.close_opt
            db.session.commit()
            
        return render_template(('muddies.html'),
                           url_string=url_string,
                           meeting=meeting,
                           muddies=muddies)
                           #g.muddy_form = MuddyForm())

@app.route('/muddies', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def muddies():
    submit_flag = 0
    if request.method == "POST":
        #results = request.g.muddy_form.getlist('vote')
        #results = request.form.getlist('vote')
        results = request.form.getlist('muddy_id')
        #if results[0]=='vote':
        print '\n\n\n results:',results
        for item in results:
            print item
            muddy = Muddy.query.get(item)
            print muddy
            muddy.like_count += 1
            submit_flag = 1
                            
        db.session.commit()
    
    g.muddy_form = MuddyForm()
    if request.method=='POST' and g.muddy_form.validate_on_submit():
        url_string = session['url_string']
        meeting = Meeting.query.filter_by(url_string=url_string).first()
        id = g.muddy_form.id.data
        
        #if (id):
            #muddy = Muddy.query.get(id)
            #muddy.like_count = g.muddy_form.like_count.data
           
            #print '\nMuddy like count:',muddy.like_count
        
        if not (id):
            if (g.muddy_form.body.data):
                print 'Muddy body:', g.muddy_form.body.data
                like_count = 0
                muddy = Muddy(g.muddy_form.body.data,g.muddy_form.meeting_id.data,like_count)

                muddy.reguser_id = meeting.reguser_id
                muddy.demo_email = meeting.demo_email
                    
                print muddy
                
                db.session.add(muddy)
                db.session.commit()
            elif submit_flag == 0:
                meeting.blank_response += 1
                db.session.commit()
                print meeting.blank_response
                print 'No muddy created...'
                return render_template('/submitted_empty.html',
                                       meeting=meeting)


        else:
            print 'Not rendered properly'
            print '\n\n',g.muddy_form.errors
            return redirect(url_for('index'))
        

        url_string = session['url_string']
        print '\n\n\nin muddies -- url_string:',session['url_string']

        #flash('Your muddy is now live!')
    #return redirect(url_for('m', url_string=session['url_string']))
    
    return render_template('/submitted.html',
                            meeting=meeting)


@app.route('/feedback_delete', methods=['GET', 'POST'])
@login_required
def feedback_delete():
    print 'Here in muddy_delete!'
    results = request.form.getlist('muddy_id')
    print 'results:',results
    for item in results:
        print 'item:',item
        if (item):
            muddy = Muddy.query.get(int(item))
            print 'muddy is:',int(item), muddy
            flash('The selected feedback (under meeting {}, course {}) has been deleted!'.format(muddy.meeting.title, muddy.meeting.course.title))
            db.session.delete(muddy)
            db.session.commit()
            return redirect(url_for('view_feedback', url_string=session['bc_url'], page=1))

#@app.route('/')
@app.route('/dl_csv_course', methods=['POST'])
@login_required
def dl_csv_course():
    print 'Here in download_csv!'
    results = request.form.getlist('id')
    print 'results:',results
    for item in results:
        print 'item:',item
        if (item):
            course = Course.query.get(int(item))
            print 'course is:',int(item), course
            reguser = Reguser.query.get(course.reguser_id)
            filename = course_dl(reguser,course)
            downloads = app.config['DOWNLOAD_FOLDER']
            print downloads, filename
            try:
                flash('Content for {} has been download!'.format(course.title))
	        return send_from_directory(directory=downloads, filename=filename, as_attachment=True)

            except Exception as file_send_error:
                return str(file_send_error)



#@app.route('/')
@app.route('/dl_csv_meeting', methods=['POST'])
@login_required
def dl_csv_meeting():
    print 'Here in download_csv!'
    results = request.form.getlist('id')
    print 'results:',results
    for item in results:
        print 'item:',item
        if (item):
            meeting = Meeting.query.get(int(item))
            print 'meeting is:',int(item), meeting
            reguser = Reguser.query.get(meeting.reguser_id)
            filename = meeting_dl(reguser,meeting)
            downloads = app.config['DOWNLOAD_FOLDER']
            print downloads, filename
            try:
                flash('Content for {} has been download!'.format(meeting.title))
	        return send_from_directory(directory=downloads, filename=filename, as_attachment=True)

            except Exception as file_send_error:
                return str(file_send_error)
            
@app.route('/send_course_view', methods=['POST'])
@login_required
def send_course_view():
    print 'Here in course_view_send_email!'
    results = request.form.getlist('id')
    print 'results:',results
    for item in results:
        print 'item:',item
        if (item):
            course = Course.query.get(int(item))
            print 'course is:',int(item), course
            reguser = Reguser.query.get(course.reguser_id)
            print  'User is:', reguser.nickname
            course_view(reguser,course)
            flash('{} details has been sent to {}'.format(course.title,g.reguser.email))
            #session['course_num'] = course.id
            #session['course_title'] = course.title
            #return redirect(url_for('view_folder'))
            return ('', 204)


            
@app.route('/send_meeting_view', methods=['POST'])
@login_required
def send_meeting_view():
    print 'Here in meeting_view_send_email!'
    results = request.form.getlist('id')
    print 'results:',results
    for item in results:
        print 'item:',item
        if (item):
            meeting = Meeting.query.get(int(item))
            print 'meeting is:',int(item), meeting
            reguser = Reguser.query.get(meeting.reguser_id)
            print  'User is:', reguser.email
            meeting_view(reguser,meeting)
            flash('{} details has been sent to {}'.format(meeting.title,g.reguser.email))
            #session['course_num'] = meeting.course_id
            #session['course_title'] = course.title
            #return redirect(url_for('view_folder'))
            return ('', 204)

@app.route('/send_form_open', methods=['POST'])
@login_required
def send_form_open():
    print 'Here in course_view_send_email!'
    results = request.form.getlist('id')
    print 'results:',results
    for item in results:
        print 'item:',item
        if (item):
            meeting = Meeting.query.get(int(item))
            #print ' is:',int(item), course
            #reguser = Reguser.query.get(course.reguser_id)
            reguser = g.reguser
            print  'User is:', reguser.nickname
            form_open(reguser.email,meeting)
            #flash('{} details has been sent to {}'.format(meeting.title,g.reguser.email))
            return ('', 204)

@app.route('/email_form_url', methods=['POST'])
@login_required
def email_form_url():
    print 'sharing URL by email'
    if request.method == "POST" and g.gen_form.validate_on_submit():
        print '\n\nHere in register beta_form3!'
        email_string = g.gen_form.inp_string.data
        meeting_id = g.gen_form.id.data
        email_list = []
        email_list_err = []
        email_list_pre_valid = email_string.split(",")
        for item in email_list_pre_valid:
            is_valid = validate_email(item)
            if (is_valid):
                email_list.append(item)
            else:
                email_list_err.append(item)
        email_list = list(set(email_list))
        #results = request.form.getlist('id')
        print 'meeting_id:',meeting_id
        print 'email_list:',email_list
        meeting = Meeting.query.get(meeting_id)
        #reguser = Reguser.query.get(meeting.reguser_id)
        reguser = g.reguser
        print  'User is:', reguser.email
        print  'valid emails:', email_list
        print 'invalid emails:', email_list_err
        #form_open(reguser.email,meeting)
        form_share_email(email_list, reguser.email,meeting)
        if len(email_list) > 0:
            flash('Form {} URL has been sent to {}'.format(meeting.title,','.join(email_list)))
        if len(email_list_err) > 0:
            flash('The following are not acceptable email ids: {}'.format(','.join(email_list_err)))

        return ('', 204)
    else:
        flash("At least one email id required. No input received")
        return('',204)
            
    

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/google_logout')
def google_logout():
    print '\n\n\n\n AAAAAAAAAAAAAAAAAAAAAA', g.reguser.id, g.reguser.email, g.reguser.social_nw
    logout_user()
    return redirect(url_for('index'))


@app.route('/reguser/<nickname>')
@app.route('/reguser/<nickname>/<int:page>')
@login_required
def reguser(nickname, page=1):
    reguser = Reguser.query.filter_by(nickname=nickname).first()
    print 'the user is:',reguser
    print '\n\n\n Here in user page'
    if reguser is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    courses = reguser.courses.paginate(page, COURSES_PER_PAGE, False)
    live_num = courses.query.filter_by(live_stat=True).count()
    archived_num = courses.query.filter_by(live_stat=False).count()
    
    print "In user view"
    return render_template('reguser.html',
                           live_num = live_num,
                           archived_num = archived_num,
                           reguser=reguser,
                           courses=courses)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.reguser.nickname)
    if form.validate_on_submit():
        g.reguser.nickname = form.nickname.data
        g.reguser.about_me = form.about_me.data
        db.session.add(g.reguser)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    elif request.method != "POST":
        form.nickname.data = g.reguser.nickname
        form.about_me.data = g.reguser.about_me
    return render_template('edit.html', form=form)


@app.route('/search', methods=['POST'])
@login_required
def search():
    print 'In search:'
    if not g.search_form.validate_on_submit():
        return ('Sorry, no results to show!')
    else:
        query=g.search_form.search.data

    print 'in search_results', 'query=',query
    results_muddy = Muddy.query.filter_by(reguser_id=g.reguser.id).whoosh_search(query, MAX_SEARCH_RESULTS).all()
    results_form = Meeting.query.filter_by(reguser_id=g.reguser.id).whoosh_search(query, MAX_SEARCH_RESULTS).all()
    results_folder = Course.query.filter_by(reguser_id=g.reguser.id).whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                           query=query,
                           results_muddy=results_muddy,
                           results_form=results_form,
                           results_folder=results_folder)


@app.route('/index', methods=['GET', 'POST'])
@app.route('/new_form', methods=['GET','POST'])
#@login_required
def new_form():
    print 'Here in new_form!'
    return render_template('new_demo_form.html')

@app.route('/new_demo_form', methods=['POST'])
def new_demo_form():
    g.demo_form = DemoForm()
    print 'In new_demo_form()'
    #results = request.demo_form.getlist('id')
    #print 'demo_form, id:', results
    if request.method == "POST" and g.demo_form.validate_on_submit():
        print 'In new_demo_form() inside'
        test_code_lite = g.demo_form.test_code_lite.data
        if test_code_lite != "test_test":
            return redirect("index.html")
        title = g.demo_form.title.data
        prompt = g.demo_form.prompt.data
        demo_email = g.demo_form.demo_email.data
        demo = Demo.query.filter_by(email=demo_email).first()

        
        print '\n\n in new_demo_form', title, prompt, demo_email
        if demo is None:
            reguser = Reguser.query.filter_by(email=demo_email).first()
            if reguser is None:
                print '\n demo is none'
                demo = Demo(demo_email)
                db.session.add(demo)
                db.session.commit()
            else:
                return render_template('redirect_account.html')
                #return redirect(url_for('index')+'#login')

        course_id = 2
        reguser_id = 1
        close_opt = 2
        live_till_hours = 14*24 #(2 weeks)
        
        meeting = Meeting(title,course_id,prompt,close_opt,live_till_hours)
        meeting.reguser_id = reguser_id
        meeting.demo_email = demo_email
        meeting.close_stat = 0
        meeting.blank_response = 0
        #meeting = Meeting_demo(title, prompt,demo_email)
        db.session.add(meeting)
        db.session.commit()
        
        form_open(meeting.demo_email,meeting)
        return render_template(('demo_form_created.html'),
                            meeting=meeting)

    else:
        return str(g.demo_form.errors)


@app.route('/get_test_code', methods=['GET','POST'])
def get_test_code():
    print 'Here in register beta_form!'
    if request.method == "POST" and g.wantbeta_form.validate_on_submit():
        print '\n\nHere in register beta_form2!'
        print 'Inside wantbeta'
        email = g.wantbeta_form.email.data
        wantbeta = Wantbeta.query.filter_by(email=email).first()
        if wantbeta is not None:
            #Send email even if it already exists!
            eoi_noted(wantbeta.email)
            return render_template('eoi_noted.html')
        else:
            wantbeta = Wantbeta(email)
            db.session.add(wantbeta)
            db.session.commit()
            eoi_noted(wantbeta.email)
            return render_template('eoi_noted.html')

@app.route('/register_beta', methods=['GET','POST'])
def register_beta():
    print 'Validating test code'
    if request.method == "POST" and g.gen_form.validate_on_submit():
        print '\n\nHere in register beta_form3!'
        test_code = g.gen_form.inp_string.data
        if test_code != "test_test":
            return str("Wrong test code. Please try again.")
        else:
            return redirect("register#login")
    else:
        print '\n\nHere in register beta_form!'
        return render_template('register_beta_form.html')

@app.route('/delete_account', methods=['POST','GET'])
@login_required
def delete_account():
    return render_template('delete_account.html')
