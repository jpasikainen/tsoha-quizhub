from db import db
from flask import session

def end_open_sessions():
    sql = "UPDATE user_answers SET session_on=FALSE WHERE user_id=:user_id"
    db.session.execute(sql, {"user_id":session["user_id"]})
    db.session.commit()

def admin_delete_quiz(quiz_id):
    sql = "UPDATE quizzes SET visible=FALSE WHERE id=:quiz_id"
    db.session.execute(sql, {"quiz_id":quiz_id})
    db.session.commit()

def get_all_visible_quizzes():
    sql = "SELECT users.username, quizzes.id, quizzes.title, quizzes.date, quizzes.upvotes, quizzes.downvotes " \
        "FROM users INNER JOIN quizzes ON users.id = quizzes.creator_id " \
        "WHERE visible=TRUE AND published=TRUE " \
        "ORDER BY date DESC"
    return db.session.execute(sql).fetchall()