from flask import session
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, FieldList, FormField, SubmitField
from wtforms.validators import DataRequired, Length
from db import db

class AnswerForm(FlaskForm):
    answer = TextField("Answer:", validators=[Length(max=50)])
    correct = BooleanField("Correct")

class QuestionForm(FlaskForm):
    question = TextField("Question:", validators=[DataRequired(), Length(min=1, max=50)])
    answers = FieldList(FormField(AnswerForm), min_entries=4)

class CreateQuizForm(FlaskForm):
    title = TextField("Quiz title:", validators=[DataRequired(), Length(min=1, max=30)])
    questions = FieldList(FormField(QuestionForm))
    submit_button = SubmitField("Publish")
    add_question_button = SubmitField("Add New Question")
    remove_question_button = SubmitField("Remove Last Question")

def initialize_form(request):
    form = CreateQuizForm()

    # Add new FieldSet if add_question_button was pressed
    if request.form.get("add_question_button"):
        form.questions.append_entry()
        return form
    elif request.form.get("remove_question_button"):
        form.questions.pop_entry()
        return form

    if not request.form.get("submit_button"):
        form.questions.append_entry()
    return form

def submit_form(data):
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