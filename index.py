from db import db
from flask import session

def admin_delete_quiz(quiz_id):
    sql = "UPDATE quizzes SET visible=FALSE WHERE id=:quiz_id"
    db.session.execute(sql, {"quiz_id":quiz_id})
    db.session.commit()

def get_all_visible_quizzes():
    sql = "SELECT users.username, quizzes.id, quizzes.title, " \
        "(date_trunc('second', NOW()::TIMESTAMP)::date - quizzes.date::date) " \
        "FROM users INNER JOIN quizzes ON users.id = quizzes.creator_id " \
        "WHERE visible=TRUE AND published=TRUE AND users.removed=FALSE " \
        "ORDER BY date DESC"
    return db.session.execute(sql).fetchall()

def get_votes(quizzes):
    votes = []
    for quiz in quizzes:
        sql = "SELECT COUNT(*) FROM votes WHERE quiz_id=:quiz_id AND liked=TRUE"
        pos_votes = db.session.execute(sql, {"quiz_id":quiz[1]}).fetchone()[0]
        sql = "SELECT COUNT(*) FROM votes WHERE quiz_id=:quiz_id"
        total_votes = db.session.execute(sql, {"quiz_id":quiz[1]}).fetchone()[0]
        if total_votes == 0: total_votes = 1
        votes.append(round(pos_votes / total_votes * 5, 1))
    return votes