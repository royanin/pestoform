from app import db, models
#u = models.User.query.filter_by(email="royanin.qn@gmail.com").first()
users = models.User.query.all()
for u in users:
    print u.id, u.nickname, u.email, u.password
"""
demo = models.Demo.query.filter_by(email="NA").first()
if demo is None:
    demo = models.Demo(email="NA")
    db.session.add(demo)
    db.session.commit()
"""
