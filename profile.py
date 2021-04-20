from db import db
from flask import session

def get_users_own_quizzes():
    sql = "SELECT users.username, quizzes.id, quizzes.title, quizzes.date, quizzes.upvotes, quizzes.downvotes, published " \
            "FROM users INNER JOIN quizzes ON users.id = quizzes.creator_id " \
            "WHERE visible=TRUE AND creator_id=:creator_id " \
            "ORDER BY date DESC"
    return db.session.execute(sql, {"creator_id":session["user_id"]}).fetchall()

def get_user_id():
    sql = "SELECT id FROM users WHERE username=:username AND removed=FALSE"
    return db.session.execute(sql, {"username":username}).fetchone()

def get_other_users_quizzes(user_id):
    sql = "SELECT users.username, quizzes.id, quizzes.title, quizzes.date, quizzes.upvotes, quizzes.downvotes " \
        "FROM users INNER JOIN quizzes ON users.id = quizzes.creator_id " \
        "WHERE visible=TRUE AND published = TRUE AND creator_id=:creator_id " \
        "ORDER BY date DESC"
    return db.session.execute(sql, {"creator_id":user_id}).fetchall()