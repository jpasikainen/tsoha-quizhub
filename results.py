from db import db
from flask import session

def get_answer_ids():
    if not session.get("quiz_id"):
        return []
    sql = "SELECT answer_id FROM user_answers " \
        "WHERE user_id=:user_id AND quiz_id=:quiz_id AND session_on=TRUE"
    answers = db.session.execute(sql, {"user_id":session["user_id"], "quiz_id":session["quiz_id"]}).fetchall()
    return [i for (i,) in answers]

def get_correct_answers_count(answer_ids):
    sql = "SELECT COUNT(*) FROM answers " \
        "WHERE id IN :answer_ids AND correct = TRUE"
    return db.session.execute(sql, {"answer_ids":tuple(answer_ids)}).fetchone()[0]

def update_user_answer_session_status(answer_ids):
    sql = "UPDATE user_answers SET session_on=FALSE " \
        "WHERE user_id=:user_id AND answer_id IN :answer_ids"
    db.session.execute(sql, {"user_id":session["user_id"], "answer_ids":tuple(answer_ids)})
    db.session.commit()

def quiz_on_session():
    sql = "SELECT COUNT(*) FROM user_answers WHERE session_on=TRUE AND user_id=:user_id"
    result = db.session.execute(sql, {"user_id":session["user_id"]}).fetchone()
    return True if result else False
    