from app import app
from flask import render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
import datetime

@app.route("/", methods=["GET", "POST"])
def index():
    # Delete button for admins, just hides the tables
    if request.method == "POST" and request.values.get("delete"):
        quiz_id = request.values.get("quiz_id")
        sql = "UPDATE quizzes SET visible=FALSE WHERE id=:quiz_id"
        db.session.execute(sql, {"quiz_id":quiz_id})
        db.session.commit()

    # Get all the info required for making a post
    # Get only visible quizzes
    sql = "SELECT users.username, quizzes.id, quizzes.title, quizzes.date, quizzes.upvotes, quizzes.downvotes " \
        "FROM users INNER JOIN quizzes ON users.id = quizzes.creator_id " \
        "WHERE visible=TRUE AND published=TRUE " \
        "ORDER BY date DESC"
    result = db.session.execute(sql).fetchall()

    # Check if user is admin and return False if the cookies is not found
    is_admin = session.get("is_admin", False)

    return render_template("index.html", quizzes=result, admin=is_admin)

@app.route("/quiz/<int:id>", methods=["GET", "POST"])
def quiz(id):
    # Get the index of the question
    question_index = int(request.values.get("index", 0))
    
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
        # Get the answers for the question
        sql = "SELECT answer, id FROM answers WHERE question_id=:question_id"
        answers = db.session.execute(sql, {"question_id":question[0]}).fetchall()
    else:
        # Quiz ended
        # Write quiz_id only after completing the quiz
        # This prevents quitting halfway through
        session["quiz_id"] = id
        return redirect("/results")

    return render_template("quiz.html", question=question[1], answers=answers, index=question_index)

@app.route("/results", methods=["POST", "GET"])
def results():
    # Redirect GET requests if no cookies otherwise display previous quiz results
    if request.method == "GET" and "quiz_id" not in session or len(session["answers"]) == 0:
        return redirect("/")

    # Get the title
    quiz_id = session["quiz_id"]
    sql = "SELECT title FROM quizzes WHERE id=:quiz_id"
    title = db.session.execute(sql, {"quiz_id":quiz_id}).fetchone()[0]

    # Check how many correct answers
    sql = "SELECT COUNT(correct), " \
        "(SELECT COUNT(correct) FROM answers WHERE id IN :answer_ids AND correct = TRUE) " \
        "FROM answers WHERE id IN :answer_ids"
    answers = db.session.execute(sql, {"answer_ids":tuple(session["answers"])}).fetchone()
    total = answers[0]
    correct = answers[1]

    # Save score
    # 100 = full points
    # Add time effect
    test_user = 1
    score = round(100 * (correct / total))
    sql = "INSERT INTO scores (user_id, quiz_id, score) VALUES (:user_id, :quiz_id, :score)"
    db.session.execute(sql, {"user_id":test_user, "quiz_id":quiz_id, "score":score})
    db.session.commit()

    return render_template("results.html", title=title, correct=correct, total=total, score=score)

@app.route("/create", methods=["POST", "GET"])
def create():
    if session.get("user_id") == None:
        return redirect("/")

    error_message = None

    if request.method == "POST":
        session["create_quiz_page"] = session.get("create_quiz_page", 1) + 1
        session["create_quiz_pages"] = session.get("create_quiz_pages", 1) + 1

        title = request.form.get("title")
        question = request.form.get("question")

        answers = []        
        corrects = []
        for i in range(4):
            answers.append(request.form.get("answer_" + str(i)))
            corrects.append(request.form.get("correct_" + str(i), False))
        #return str(session["quiz_id"])
        if session.get("create_quiz_id", None) == None:
            sql = "INSERT INTO quizzes (creator_id, title) VALUES(:creator_id, :title) RETURNING id"
            quiz_id = db.session.execute(sql, {"creator_id":session["user_id"], "title":title}).fetchone()[0]
            db.session.flush()
            session["create_quiz_id"] = quiz_id

        sql = "INSERT INTO questions (quiz_id, question) VALUES(:quiz_id, :question) RETURNING id"
        question_id = db.session.execute(sql, {"quiz_id":session["create_quiz_id"], "question":question}).fetchone()[0]
        db.session.flush()

        for i in range(4):
            answer = answers[i]
            if answer == None or answer == "" or answer == " ":
                continue
            correct = corrects[i]

            sql = "INSERT INTO answers (question_id, answer, correct) VALUES(:question_id, :answer, :correct)"
            db.session.execute(sql, {"question_id":question_id, "answer":answer, "correct":correct})
            db.session.flush()
        db.session.commit()

        if request.form.get("publish"):
            sql = "UPDATE quizzes SET published=TRUE WHERE id=:quiz_id"
            db.session.execute(sql, {"quiz_id":session["create_quiz_id"]})
            db.session.commit()

            session.pop("create_quiz_id", None)
            session.pop("create_quiz_page", None)
            session.pop("create_quiz_pages", None)
            return redirect("/")
        return render_template("create.html", title=title)
    return render_template("create.html")

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
            error_message = "Incorrect username"
        else:
            hash_value = user[0]
            if check_password_hash(hash_value, password):
                session["username"] = username
                session["is_admin"] = user[1]
                session["user_id"] = user[2]
                return redirect("/")
            else:
                error_message = "Incorrect password"

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
        return redirect("/")
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    # Logout
    if session.get("username"):
        session.pop("username", None)
        session.pop("is_admin", None)
        session.pop("user_id", None)
        return render_template("logout.html")
    return redirect("/")

@app.route("/profile/<string:username>", methods=["POST", "GET"])
def profile(username):
    if session.get("user_id"):
        result = []
        if session["username"] == username:
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
    return redirect("/")