from app import app
from flask import render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
import datetime

@app.route("/", methods=["GET", "POST"])
def index():
    # Delete button for admins, just hides the tables
    if request.method == "POST" and request.values.get("delete"):
        quiz_id = int(request.values.get("quiz_id"))
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
    is_admin = request.values.get("is_admin", False)

    return render_template("index.html", quizzes=result, admin=is_admin)

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
    # One of the buttons is pressed
    if request.method == "POST":
        # Create a quiz and save the id
        if request.values.get("title"):
            sql = "INSERT INTO quizzes (creator_id, title) " \
                "VALUES (:creator_id, :title) " \
                "RETURNING id"
            result = db.session.execute(sql, {"creator_id":1, "title":request.form["title"]})
            db.session.flush()

            quiz_id = result.fetchone()[0]
            session["quiz_id"] = quiz_id
            
        sql = "INSERT INTO questions (quiz_id, question) VALUES (:quiz_id, :question) " \
            "RETURNING id"
        result = db.session.execute(sql, {"quiz_id":session["quiz_id"], "question":request.form["question"]})
        db.session.flush()

        question_id = result.fetchone()[0]

        for i in range(1, 5):
            # If empty, drop
            if request.values.get("answer_" + str(i)) == "":
                continue
            answer = request.form["answer_" + str(i)]
            correct = False
            if "correct_" + str(i) in request.form.keys():
                correct = True
            sql = "INSERT INTO answers (question_id, answer, correct) " \
                "VALUES (:question_id, :answer, :correct)"
            db.session.execute(sql, {"question_id":question_id, \
                "answer":answer, "correct":correct})
            db.session.flush()
        db.session.commit()

        if "publish" in request.form:
            sql = "UPDATE quizzes SET published=TRUE WHERE id=:quiz_id"
            db.session.execute(sql, {"quiz_id":session["quiz_id"]})
            db.session.commit()
            return redirect("/")

        return render_template("create.html", title_page=False)

    return render_template("create.html", title_page=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    # Redirect logged in users
    if session.get("username"):
        return redirect("/profile/" + session["username"])

    # Login
    if request.method == "POST":
        # Check that all the fields are filled
        if not request.values.get("username") or not request.values.get("password"):
            return render_template("login.html", error_message="Please fill all the fields")

        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT password, admin FROM users WHERE username=:username"
        user = db.session.execute(sql, {"username":username}).fetchone()
        
        if user == None:
            return "Incorrect username"
        else:
            hash_value = user[0]
            if check_password_hash(hash_value, password):
                session["username"] = username
                session["is_admin"] = user[1]
            else:
                return "Incorrect password"

        return redirect("/")
    return render_template("login.html")

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
        return render_template("logout.html")
    return redirect("/")