from app import db, models
u = models.User.query.filter_by(email="royanin.qn@gmail.com").first()
print u.id, u.nickname, u.email
db.session.delete(u)
db.session.commit()
