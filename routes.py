from app import app
from flask import render_template, request, session
from db import db

@app.route("/")
def index():
    sql = "SELECT * FROM quizzes"
    result = db.session.execute(sql).fetchall()
    return render_template("index.html", quizzes=result)

@app.route("/quiz/<int:id>", methods=["GET", "POST"])
def quiz(id):
    # Get the index of the question
    question_index = 0
    if request.values.get("index") != None:
        question_index = int(request.values.get("index"))
    
    # Save answers
    if question_index != 0:
        user_answer = int(request.values.get("user_answer")) - 1
        session[str(question_index)] = user_answer

    # Get the question of the index
    sql = "SELECT id, question FROM questions WHERE quiz_id=:id LIMIT 1 OFFSET :question_index"
    question = db.session.execute(sql, {"id":id, "question_index":question_index}).fetchone()

    answers = []
    # Get the answers if there is a question 
    if question != None:
        question_id = question[0]

        # Get the answers for the question
        sql = "SELECT answer FROM answers WHERE question_id=:question_id"
        answers = db.session.execute(sql, {"question_id":question_id}).fetchall()

    return render_template("quiz.html", question=question, answers=answers, index=question_index)