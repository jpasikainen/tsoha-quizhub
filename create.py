from flask import session
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, FieldList, FormField, SubmitField
from wtforms.validators import DataRequired
from db import db

class AnswerForm(FlaskForm):
    answer = TextField("Answer:")
    correct = BooleanField("Correct")

class QuestionForm(FlaskForm):
    question = TextField("Question:", validators=[DataRequired()])
    answers = FieldList(FormField(AnswerForm), min_entries=4)

class CreateQuizForm(FlaskForm):
    title = TextField("Quiz title:", validators=[DataRequired()])
    questions = FieldList(FormField(QuestionForm))
    submit_button = SubmitField("Publish")
    add_quiz_button = SubmitField("Add New Question")
    
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions")
        super(CreateQuizForm, self).__init__(*args, **kwargs)
        self.questions.min_entries = questions

def initialize_form(request):
    # Add new FieldSet if add_quiz_button was pressed and save it to a cookie
    if request.form.get("add_quiz_button", None):
        session["question_count"] = session.get("question_count", 1) + 1
        # Create question_count amount of sets
        form = CreateQuizForm(questions=session.get("question_count", 1))
        # Add new set if necessary
        form.questions.append_entry()
        return form
    
    form = CreateQuizForm(questions=1)
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