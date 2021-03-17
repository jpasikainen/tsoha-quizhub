from app import app
from flask import render_template, request
from db import db

@app.route("/")
def index():
    sql = "SELECT * FROM quizzes"
    result = db.session.execute(sql).fetchall()
    return render_template("index.html", quizzes=result)

@app.route("/quiz/<int:id>", methods=["GET", "POST"])
def quiz(id):
    sql = "SELECT * FROM questions WHERE quiz_id=:id"
    questions = db.session.execute(sql, {"id":id}).fetchall()
    
    index = 0
    if request.values.get("index") != None:
        index = int(request.values.get("index")) + 1

    answers = []
    if index < len(questions):
        question_id = questions[index][0]
        sql = "SELECT answer FROM answers WHERE question_id=:index"
        answers = db.session.execute(sql, {"index":question_id}).fetchall()
        
    return render_template("quiz.html", quiz=questions, answers=answers, index=index)