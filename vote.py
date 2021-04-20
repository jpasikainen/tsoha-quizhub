from db import db
from flask import session

def has_voted():
    sql = "SELECT COUNT(*) FROM votes WHERE user_id=:user_id AND quiz_id=:quiz_id"
    return db.session.execute(sql, {"user_id":session["user_id"], "quiz_id":session["quiz_id"]}).fetchone()[0]

def add_vote(liked):
    sql = "INSERT INTO votes (user_id, quiz_id, liked) VALUES(:user_id, :quiz_id, :liked)"
    db.session.execute(sql, {"quiz_id":session["quiz_id"], "user_id":session["user_id"], "liked":liked})
    db.session.commit()

def change_vote(liked):
    sql = "UPDATE votes SET liked=:liked WHERE user_id=:user_id AND quiz_id=:quiz_id"
    db.session.execute(sql, {"quiz_id":session["quiz_id"], "user_id":session["user_id"], "liked":liked})
    db.session.commit()