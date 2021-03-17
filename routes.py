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
        user_answer_id = int(request.values.get("user_answer_id"))
        temp = session["answers"]
        temp.append(user_answer_id)
        session["answers"] = temp
    else:
        session["answers"] = []

    # Get the question of the index
    sql = "SELECT id, question FROM questions WHERE quiz_id=:id LIMIT 1 OFFSET :question_index"
    question = db.session.execute(sql, {"id":id, "question_index":question_index}).fetchone()

    answers = []
    # Get the answers if there is a question 
    if question != None:
        question_id = question[0]

        # Get the answers for the question
        sql = "SELECT answer, id FROM answers WHERE question_id=:question_id"
        answers = db.session.execute(sql, {"question_id":question_id}).fetchall()
    else:
        session["quiz_id"] = id

    return render_template("quiz.html", question=question, answers=answers, index=question_index)

@app.route("/results", methods=["POST"])
def results():
    # Get title
    quiz_id = session["quiz_id"]
    sql = "SELECT title FROM quizzes WHERE id=:quiz_id"
    title = db.session.execute(sql, {"quiz_id":quiz_id}).fetchone()[0]

    # Check how many correct answers
    #answer_ids = ", ".join(str(item) for item in session["answers"])
    sql = "SELECT correct FROM answers WHERE id IN :answer_ids"
    answers = db.session.execute(sql, {"answer_ids":tuple(session["answers"])}).fetchall()
    total = len(answers)
    correct = 0
    for answer in answers:
        if answer[0] == True:
            correct += 1

    return render_template("results.html", title=title, correct=correct, total=total)
    
