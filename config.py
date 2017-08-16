import os
from instances import OAUTH_CREDENTIALS, GGL_CREDENTIALS
basedir = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_FOLDER =  os.path.join(basedir, 'file_serve/') 

CSRF_ENABLED = True
SECRET_KEY = os.environ.get('DB_SECRET_KEY')
SECURITY_REGISTERABLE = True
SECURITY_CONFIRM_ERROR_VIEW = '/login_error_redirect'
#SECURITY_PASSWORD_HASH = 'plaintext'
#SECURITY_PASSWORD_SALT = 'sha512_crypt'
#SECURITY_CONFIRMABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
#SECURITY_PASSWORDLESS = True
#SECURITY_TOKEN_AUTHENTICATION_KEY = 'auth_token'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
WHOOSH_BASE = os.path.join(basedir, 'search.db')

#Social Login
OAUTH_CREDENTIALS = OAUTH_CREDENTIALS
GOOGLE_CLIENT_ID = GGL_CREDENTIALS['GOOGLE_CLIENT_ID']

# mail server settings
MAIL_SERVER = 'smtp.zoho.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = [MAIL_USERNAME]

# pagination
COURSES_PER_PAGE = 8
MEETINGS_PER_PAGE = 25
FEEDBACK_PER_PAGE = 30
MAX_SEARCH_RESULTS = 50
SORTING_TYPE = ['Form NEWest first','Form OLDest first', 'Folder OLDest first','Folder NEWest first','Folder with MOST feedback first','Folder with FEWEST feedback first']

#site names:
PROD_SITE = os.environ.get('PROD_SITE')
DEV_SITE = os.environ.get('DEV_SITE')
SITE = DEV_SITE
