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

    # Get the question of the index
    sql = "SELECT id, question FROM questions WHERE quiz_id=:id LIMIT 1 OFFSET :question_index"
    question = db.session.execute(sql, {"id":id, "question_index":question_index}).fetchone()
    question_id = None
    if question != None:
        question_id = question[0]

    # Get the answers for the question
    sql = "SELECT answer, correct FROM answers WHERE question_id=:question_id"
    answers = db.session.execute(sql, {"question_id":question_id}).fetchall()

    return render_template("quiz.html", question=question, answers=answers, index=question_index)

def quizlegacy(id):
    sql = "SELECT * FROM questions WHERE quiz_id=:id"
    questions = db.session.execute(sql, {"id":id}).fetchall()
    
    index = 0
    if request.values.get("index") != None:
        index = int(request.values.get("index")) + 1

    answers = []
    if index < len(questions):
        question_id = questions[index][0]
        sql = "SELECT answer, question_id FROM answers WHERE question_id=:index"
        answers = db.session.execute(sql, {"index":question_id}).fetchall()
        
        if request.values.get("user_answer") != None:
            # Loop index starts from 1
            user_answer = int(request.values.get("user_answer")) - 1
            #return str(answers)
            # Write user's answers in a cookie
            # Overwritten in each quiz
            # Format; question index: chosen answer
            session[str(index - 1)] = user_answer
    
    return render_template("quiz.html", quiz=questions, answers=answers, index=index)