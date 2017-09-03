def first_time():
    from app import db, models
    from flask_security import login_user, logout_user, current_user, login_required
    from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    user = models.User.query.filter_by(email='royanin.qn@gmail.com').first()
    if not (user):
        user_datastore.create_user(email='royanin.qn@gmail.com',password='complex123#')
        db.session.commit()
        user = models.User.query.filter_by(email='royanin.qn@gmail.com').first()
        g.user = user
        course1 = models.Course(title="Uncategorized",level=0)
        course2 = models.Course(title="All_demo_forms",level=0)
        db.session.add(course1)
        db.session.add(course2)        
        db.session.commit()
        for course in g.user.courses:
            print user.email, course.title
    else:
        print user.id, user.email
    demo = models.Demo.query.filter_by(email="NA").first()
    if demo is None:
        demo = models.Demo(email="NA")
        db.session.add(demo)
        db.session.commit()
    else:
        print demo.id, demo.email

if __name__ == '__main__':
    first_time()
