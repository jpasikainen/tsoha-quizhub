from db import db
from flask import session

def end_open_sessions():
    sql = "UPDATE user_answers SET session_on=FALSE WHERE user_id=:user_id AND quiz_id=:quiz_id"
    db.session.execute(sql, {"user_id":session["user_id"], "quiz_id":session["quiz_id"]})
    db.session.commit()

def save_answer(user_answer_id, quiz_id):
    question_id = session["quiz_question_id"]
    user_id = session["user_id"]

    sql = "INSERT INTO user_answers (user_id, quiz_id, answer_id) " \
        "VALUES(:user_id, :quiz_id, :answer_id)"
    db.session.execute(sql, {"user_id":user_id, "quiz_id":quiz_id, "answer_id":user_answer_id })
    db.session.commit()

def get_question(quiz_id, question_index):
    sql = "SELECT id, question FROM questions WHERE quiz_id=:quiz_id " \
        "LIMIT 1 OFFSET :offset"
    return db.session.execute(sql, {"quiz_id":quiz_id, "offset":question_index}).fetchone()

def get_answers(question_id):
    # Get the answers
    sql = "SELECT id, answer FROM answers WHERE question_id=:question_id"
    return db.session.execute(sql, {"question_id":question_id}).fetchall()