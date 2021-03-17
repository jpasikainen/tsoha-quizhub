from app import app
from flask import render_template, request, session, redirect
from db import db
import datetime

@app.route("/")
def index():
    # Get all the info required for making a post
    sql = "SELECT users.username, quizzes.id, quizzes.title, quizzes.date, quizzes.upvotes, quizzes.downvotes " \
        "FROM users INNER JOIN quizzes ON users.id = quizzes.creator_id"
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
        # Save starting time
        session["start_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Reset answers
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
        # Quiz ended
        # Write quiz_id only after completing the quiz
        # This prevents quitting halfway through
        session["quiz_id"] = id
        return redirect("/results")

    return render_template("quiz.html", question=question, answers=answers, index=question_index)

@app.route("/results", methods=["POST", "GET"])
def results():
    # Redirect GET requests if no cookies otherwise display previous quiz results
    if request.method == "GET" and "quiz_id" not in session:
        return redirect("/")

    # Get the title
    quiz_id = session["quiz_id"]
    sql = "SELECT title FROM quizzes WHERE id=:quiz_id"
    title = db.session.execute(sql, {"quiz_id":quiz_id}).fetchone()[0]

    # Check how many correct answers
    sql = "SELECT correct FROM answers WHERE id IN :answer_ids"
    answers = db.session.execute(sql, {"answer_ids":tuple(session["answers"])}).fetchall()
    total = len(answers)
    correct = 0
    for answer in answers:
        if answer[0] == True:
            correct += 1

    # Save score
    # 100 = full points
    # Multiply 
    test_user = 1
    score = round(100 * (correct / total))
    sql = "INSERT INTO scores (user_id, quiz_id, score) VALUES (:user_id, :quiz_id, :score)"
    db.session.execute(sql, {"user_id":test_user, "quiz_id":quiz_id, "score":score})
    db.session.commit()

    return render_template("results.html", title=title, correct=correct, total=total, score=score)
    
@app.route("/create")
def create():
    return render_template("create.html")