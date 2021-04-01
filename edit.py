from flask import session
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, FieldList, FormField, SubmitField
from wtforms.validators import DataRequired
from db import db
from werkzeug.datastructures import MultiDict

class AnswerForm(FlaskForm):
    answer = TextField("Answer:")
    correct = BooleanField("Correct")

class QuestionForm(FlaskForm):
    question = TextField("Question:", validators=[DataRequired()])
    answers = FieldList(FormField(AnswerForm), min_entries=4)

class CreateQuizForm(FlaskForm):
    title = TextField("Quiz title:", validators=[DataRequired()])
    questions = FieldList(FormField(QuestionForm))
    submit_button = SubmitField("Save Changes")
    add_question_button = SubmitField("Add New Question")
    remove_question_button = SubmitField("Remove Last Question")

def initialize_form(request, id):
    # Populate fields
    form = CreateQuizForm()
    if id:
        form = populate(id)

    # Add new FieldSet if add_question_button was pressed
    if request.form.get("add_question_button"):
        form.questions.append_entry()
        return form
    elif request.form.get("remove_question_button"):
        form.questions.pop_entry()
        return form

    return form

def populate(id):
    sql = "SELECT title FROM quizzes WHERE id=:quiz_id"
    title = db.session.execute(sql, {"quiz_id":id}).fetchone()[0]
    form = CreateQuizForm(title=title)

    sql = "SELECT id, question FROM questions WHERE quiz_id=:quiz_id"
    questions = db.session.execute(sql, {"quiz_id":id}).fetchall()
    
    for question in questions:
        question_text = question[1]
        sql = "SELECT answer, correct FROM answers WHERE question_id=:question_id"
        answers = db.session.execute(sql, {"question_id":question[0]}).fetchall()
        answers_data = []
        for answer in answers:
            answers_data.append({"answer":answer[0], "correct":answer[1]})
        
        form.questions.append_entry({"question":question_text, "answers":answers_data})

    return form

def save_form(data):
    # It is much easier to delete the old quiz and replace it with a new entry
    sql = "UPDATE quizzes SET published=FALSE, visible=FALSE WHERE id=:quiz_id"
    db.session.execute(sql, {"quiz_id":session["edit_quiz_id"]})
    db.session.flush()
    session.pop("edit_quiz_id")

    title = data["title"]
    questions_data = data["questions"]

    # Create quiz and mark it as published
    sql = "INSERT INTO quizzes (creator_id, title, published) VALUES(:creator_id, :title, TRUE) RETURNING id"
    quiz_id = db.session.execute(sql, {"creator_id":session["user_id"], "title":title}).fetchone()[0]
    db.session.flush()
    
    for entry in questions_data:
        question = entry["question"]
        
        sql = "INSERT INTO questions (quiz_id, question) VALUES(:quiz_id, :question) RETURNING id"
        question_id = db.session.execute(sql, {"quiz_id":quiz_id, "question":question}).fetchone()[0]
        db.session.flush()

        for idx, choice in enumerate(entry["answers"]):
            answer = choice["answer"]
            if answer == "":
                continue
                
            correct = choice["correct"]
            # Force the first answer to be true because it's disabled and
            # will not appear as true in data
            if idx == 0:
                correct = True
            
            sql = "INSERT INTO answers (question_id, answer, correct) VALUES(:question_id, :answer, :correct)"
            db.session.execute(sql, {"question_id":question_id, "answer":answer, "correct":correct})
            db.session.flush()
    
    db.session.commit()