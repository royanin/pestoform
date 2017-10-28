from app import db, models
u = models.Reguser.query.filter_by(email="anindyar@mit.edu").first()
print u.nickname, u.email
#db.session.delete(u)
#db.session.commit()
#users = models.Reguser.query.all()
#for u in users:
#    print u.id, u.nickname, u.email, u.password
"""
demo = models.Demo.query.filter_by(email="NA").first()
if demo is None:
    demo = models.Demo(email="NA")
    db.session.add(demo)
    db.session.commit()
"""
