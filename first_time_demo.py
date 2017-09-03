def first_time():
    from app import db, models
    from flask_security import login_user, logout_user, current_user, login_required
    from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    user = models.User.query.filter_by(email='royanin.qn@gmail.com').first()
    demo = models.Demo.query.filter_by(email="NA").first()
    if demo is None:
        demo = models.Demo(email="NA")
        db.session.add(demo)
        db.session.commit()
    else:
        print demo.id, demo.email

if __name__ == '__main__':
    first_time()
