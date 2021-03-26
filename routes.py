from app import app
from flask import render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
from datetime import datetime

from create import initialize_form, submit_form
from index import admin_delete_quiz, get_all_visible_quizzes, end_open_sessions
from quiz import save_answer, get_question, get_answers
from results import get_answer_ids, get_correct_answers_count, update_user_answer_session_status, quiz_on_session

@app.route("/", methods=["GET", "POST"])
def index():
    # End open sessions
    if session.get("user_id"):
        end_open_sessions()
    
    # Delete button for admins, just hides the tables
    if request.method == "POST" and request.values.get("delete"):
        admin_delete_quiz(request.values.get("quiz_id"))

    # Get all the info required for making a post
    # Get only visible quizzes
    result = get_all_visible_quizzes()

    # Check if user is admin and return False if the cookie is not found
    is_admin = session.get("is_admin", False)

    return render_template("index.html", quizzes=result, admin=is_admin)

@app.route("/quiz/<int:id>", methods=["GET", "POST"])
def quiz(id):
    # Must be logged in
    if not session.get("user_id"):
        return redirect("/")

    # Get the index of the question
    question_index = int(request.values.get("question_index", 0))

    # Save the answer
    if question_index != 0:
        user_answer_id = int(request.values.get("user_answer_id"))
        save_answer(user_answer_id, id)
    session["previous_question_index"] = question_index
    
    # Get the question
    question = get_question(id, question_index)
    
    # Get answers and increase index if there's a question
    if question:
        session["previous_question_id"] = session.get("quiz_question_id", None)
        session["quiz_question_id"] = question[0]
        answers = get_answers(question[0])
        question_index += 1
    else:
        session.pop("previous_question_id", None)
        session["quiz_id"] = id
        return redirect("/results", code=307)

    return render_template("quiz.html", question_index=question_index, question=question, answers=answers)

@app.route("/results", methods=["POST"])
def results():
    # Redirect non logged in users
    if session.get("user_id", None) == None and request.method == "POST":
        return redirect("/")
    
    # Get answer ids
    answer_ids = get_answer_ids()
    if len(answer_ids) == 0:
        return redirect("/")

    # Get the count of correct answers
    corrects = get_correct_answers_count(answer_ids)
    total = len(answer_ids)
    score = round(100 * (corrects / total))

    update_user_answer_session_status(answer_ids)

    return render_template("results.html", correct=corrects, total=total, score=score)
        
@app.route("/create", methods=["POST", "GET"])
def create():
    # User is not logged in
    if session.get("user_id", None) == None:
        return redirect("/")

    # Initialize form html
    form = initialize_form(request)

    # Validate form on submit
    # Doesn't activate if add_quiz_button was pressed because it creates a new set
    # which is not valid
    if form.validate_on_submit():
        data = form.data
        submit_form(data)
        return redirect("/")

    return render_template("create.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    # Redirect logged in users
    if session.get("username"):
        return redirect("/profile/" + session["username"])

    error_message = None
    # Login
    if request.method == "POST":
        # Check that all the fields are filled
        if not request.values.get("username") or not request.values.get("password"):
            return render_template("login.html", error_message="Please fill all the fields")

        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT password, admin, id FROM users WHERE username=:username"
        user = db.session.execute(sql, {"username":username}).fetchone()
        
        if user == None:
            error_message = "Incorrect username or password"
        else:
            hash_value = user[0]
            if check_password_hash(hash_value, password):
                session["username"] = username
                session["is_admin"] = user[1]
                session["user_id"] = user[2]
                return redirect("/")
            else:
                error_message = "Incorrect username or password"

    return render_template("login.html", error_message=error_message)

@app.route("/register", methods=["GET", "POST"])
def register():
    # Register
    if request.method == "POST":
        # Check that all the fields are filled
        if not request.values.get("username") or not request.values.get("password"):
            return render_template("register.html", error_message="Please fill all the fields")
        
        # Check if username exists already
        username = request.form["username"]
        sql = "SELECT COUNT(:username) FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username}).fetchone()[0]
        
        if result != 0:
            error_message = "Username has been taken. Try another one"
            return render_template("register.html", error_message=error_message)

        password = request.form["password"]

        hash_value = generate_password_hash(password)
        sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
        db.session.execute(sql, {"username":username, "password":hash_value})
        db.session.commit()
        return redirect("/login")
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    # Logout and clear the session
    if session.get("username"):
        session.clear()
        return render_template("logout.html")
    return redirect("/")

@app.route("/profile/<string:username>", methods=["POST", "GET"])
def profile(username):
    result = []
    if session.get("user_id") and session["username"] == username:
        sql = "SELECT users.username, quizzes.id, quizzes.title, quizzes.date, quizzes.upvotes, quizzes.downvotes, published " \
        "FROM users INNER JOIN quizzes ON users.id = quizzes.creator_id " \
        "WHERE visible=TRUE AND creator_id=:creator_id " \
        "ORDER BY date DESC"
        result = db.session.execute(sql, {"creator_id":session["user_id"]}).fetchall()
    else:
        sql = "SELECT id FROM users WHERE username=:username"
        user_id = db.session.execute(sql, {"username":username}).fetchone()[0]

        sql = "SELECT users.username, quizzes.id, quizzes.title, quizzes.date, quizzes.upvotes, quizzes.downvotes " \
        "FROM users INNER JOIN quizzes ON users.id = quizzes.creator_id " \
        "WHERE visible=TRUE AND published = TRUE AND creator_id=:creator_id " \
        "ORDER BY date DESC"
        result = db.session.execute(sql, {"creator_id":user_id}).fetchall()

    return render_template("profile.html", quizzes=result)