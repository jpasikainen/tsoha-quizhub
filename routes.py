from app import app
from flask import render_template, request, session, redirect, url_for
from db import db
import random

import index as index_functions
import results as results_functions
import quiz as quiz_functions
import create as create_form
import login as login_form
import register as register_form
import edit as edit_form
import profile as profile_functions
import remove_profile as remove_profile_functions
import vote as vote_functions

@app.route("/", methods=["GET", "POST"])
def index():    
    # Delete button for admins, just hides the tables
    if request.method == "POST" and request.values.get("delete"):
        index_functions.admin_delete_quiz(request.values.get("quiz_id"))

    # Get all the info required for making a post
    # Get only visible quizzes
    result = index_functions.get_all_visible_quizzes()

    # Check if user is admin and return False if the cookie is not found
    is_admin = session.get("is_admin", False)

    votes = index_functions.get_votes(result)

    return render_template("index.html", quizzes=result, admin=is_admin, votes=votes)

@app.route("/quiz/<int:id>", methods=["GET", "POST"])
def quiz(id):
    # Must be logged in
    if not session.get("user_id"):
        return redirect("/")

    session["quiz_id"] = id
    
    # Get the index of the question
    question_index = int(request.values.get("question_index", 0))
    if question_index == 0:
        session.pop("previous_question_index", None)
        # End open sessions
        quiz_functions.end_open_sessions()

    # Save the answer if it hasn't already been saved
    if question_index != 0 and session.get("previous_question_index", None) != question_index:
        user_answer_id = int(request.values.get("user_answer_id"))
        quiz_functions.save_answer(user_answer_id, id)
    session["previous_question_index"] = question_index
    
    # Get the question
    question = quiz_functions.get_question(id, question_index)
    
    # Get answers and increase index if there's a question
    if question:
        question_index += 1
        session["quiz_question_id"] = question[0]
        answers = quiz_functions.get_answers(question[0])
        random.shuffle(answers)
    else:
        return redirect("/results")

    return render_template("quiz.html", question_index=question_index, question=question, answers=answers)

@app.route("/results", methods=["GET", "POST"])
def results():
    # Redirect non logged in users
    if session.get("user_id", None) == None:
        return redirect("/")
    
    # Get answer ids
    answer_ids = results_functions.get_answer_ids()
    if len(answer_ids) == 0:
        return redirect("/")

    # Get the count of correct answers
    corrects = results_functions.get_correct_answers_count(answer_ids)
    total = len(answer_ids)
    score = round(100 * (corrects / total))

    results_functions.update_user_answer_session_status(answer_ids)

    stats = results_functions.get_all_results()

    return render_template("results.html", correct=corrects, total=total, score=score, stats=stats)
        
@app.route("/create", methods=["POST", "GET"])
def create():
    # User is not logged in
    if session.get("user_id", None) == None:
        return redirect("/")

    # Initialize form html
    form = create_form.initialize_form(request)

    # Validate form on submit
    # Doesn't activate if add_quiz_button was pressed because it creates a new set
    # which is not valid
    if request.form.get("submit_button") and form.validate_on_submit():
        data = form.data
        create_form.submit_form(data)
        return redirect("/")

    return render_template("create.html", form=form)

@app.route("/edit", methods=["POST", "GET"])
def edit():
    # User is not logged in
    if session.get("user_id", None) == None:
        return redirect("/")
    
    id = request.values.get("quiz_id")
    if id:
        session["edit_quiz_id"] = id

    form = edit_form.initialize_form(request, id)

    if request.form.get("submit_button") and form.validate_on_submit():
        data = form.data
        edit_form.save_form(data)
        return redirect("/")

    return render_template("edit.html", form=form, data=form.data)

@app.route("/login", methods=["GET", "POST"])
def login():
    # Redirect logged in users
    if session.get("username"):
        return redirect("/profile/" + session["username"])

    # Initialize form
    form = login_form.initialize_form()
    
    # Login
    if request.method == "POST":
        # Check that all the fields are filled
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            if login_form.login_successful(username, password):
                return redirect("/")

    return render_template("login.html", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    # Redirect logged in users
    if session.get("username"):
        return redirect("/profile/" + session["username"])
    
    # Initialize form
    form = register_form.initialize_form()

    # Register
    if request.method == "POST":
        # Check that all the fields are filled
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            # Check if username exists already
            if register_form.username_is_valid(username):
                register_form.save_credentials(username, password)
                return redirect(url_for("login"))        
    
    return render_template("register.html", form=form)

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
    if session.get("user_id", None) != None and session["username"] == username:
        result = profile_functions.get_users_own_quizzes()
        return render_template("profile.html", quizzes=result, can_remove=True, username=username)
    else:
        user_id = profile_functions.get_user_id()

        if user_id == None:
            return redirect("/")

        result = profile_functions.get_other_users_quizzes(user_id[0])

    return render_template("profile.html", quizzes=result, username=username)

@app.route("/remove_profile", methods=["POST"])
def remove_profile():
    if session.get("user_id", None) == None:
        return redirect("/")
    remove_profile_functions.remove_profile()
    return redirect("/")

@app.route("/vote", methods=["POST"])
def vote():
    if not session.get("user_id"):
        return redirect("/")
    
    liked = False
    if request.form.get("upvote"):
        liked = True
    
    # Check if there is an answer already
    has_voted = vote_functions.has_voted()

    if has_voted:
        vote_functions.change_vote(liked)
    else:
        vote_functions.add_vote(liked)
    
    return redirect("/")