from db import db

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