from db import db
from flask import session

def remove_profile():
    sql = "UPDATE users SET removed=TRUE WHERE id=:user_id"
    db.session.execute(sql, {"user_id":session["user_id"]})
    db.session.commit()
    session.clear()