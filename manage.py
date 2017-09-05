#!env/bin/python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from instances import ENV_VAR

from app import app
app.config['SQLALCHEMY_DATABASE_URI'] = ENV_VAR['DATABASE_URL'] 

db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.create_all()

manager = Manager(app)
manager.add_command('db', MigrateCommand)

#from app.models import User

if __name__ == '__main__':
    manager.run()
