import os
from instances import OAUTH_CREDENTIALS, GGL_CREDENTIALS, ENV_VAR
basedir = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_FOLDER =  os.path.join(basedir, 'file_serve/') 

CSRF_ENABLED = True
SECRET_KEY = ENV_VAR['DB_SECRET_KEY']
SECURITY_REGISTERABLE = True
SECURITY_CONFIRM_ERROR_VIEW = '/login_error_redirect'
SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
SECURITY_PASSWORD_SALT = ENV_VAR['SEC_PASSWD_SALT']
SECURITY_CONFIRMABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_EMAIL_SENDER = ENV_VAR['MAIL_USERNAME']
#SECURITY_PASSWORDLESS = True
#SECURITY_TOKEN_AUTHENTICATION_KEY = 'auth_token'
SECURITY_MSG_LOGIN = "",""

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True
WHOOSH_BASE = os.path.join(basedir, 'search.db')

#Social Login
OAUTH_CREDENTIALS = OAUTH_CREDENTIALS
GOOGLE_CLIENT_ID = GGL_CREDENTIALS['GOOGLE_CLIENT_ID']

# mail server settings
MAIL_SERVER = 'smtp.zoho.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = ENV_VAR['MAIL_USERNAME']
MAIL_PASSWORD = ENV_VAR['MAIL_PASSWORD']
MAIL_DEBUG = True

# administrator list
ADMINS = [MAIL_USERNAME]
URGENT_EMAIL = ENV_VAR['URGENT_EMAIL']

#Site name for general use:
WSNAME = "pestoform.com"

# pagination
COURSES_PER_PAGE = 8
MEETINGS_PER_PAGE = 25
FEEDBACK_PER_PAGE = 30
MAX_SEARCH_RESULTS = 50
SORTING_TYPE = ['Form NEWest first','Form OLDest first', 'Folder OLDest first','Folder NEWest first','Folder with MOST feedback first','Folder with FEWEST feedback first']

PROD = True

if PROD == True:
    SQLALCHEMY_DATABASE_URI = ENV_VAR['DATABASE_URL']
    SITE = ENV_VAR['PROD_SITE']
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SITE = ENV_VAR['DEV_SITE']


