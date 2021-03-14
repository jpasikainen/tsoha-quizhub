# Quizhub
Database project built with Flask and PostgreSQL for hy-tsoha.

## Description
- Twitter like feed where posts are quizzes
- A quiz consists of questions and multiple answers to choose from
- After the quiz is over, the user can rate the quiz and is rewarded points based on the speed and accuracy
- All the users can create and take part in quizzes
- Admins can remove quizzes and users

## Views
**Bolded** tasks are main features.

### Feed
- [ ] **Display quizzes in creation order**
- [ ] **Open quiz on click**
- [ ] **Create quiz button**
- [ ] Add sorting
- [ ] Add search

### Quiz
- [ ] **Opens to a new page**
- [ ] **Display question and multiple choices**
- [ ] **Add timer**
- [ ] **Reward points after completion**
- [ ] **Rate quiz**
- [ ] **Add comments**
- [ ] Correct/Incorrect answers per question

### Create user
- [ ] **Form with username and password fields**
- [ ] **On submit check if username is taken**
- [ ] **Hash password before saving**

### Login
- [ ] **Form with username and password fields**
- [ ] **On submit check if password hash is correct and login**

### Create quiz
- [ ] **Quiz name**
- [ ] **Add question and up to 4 answers choices**
- [ ] **Ability add multiple questions**
- [ ] Add tags
- [ ] Human verification before publishing

### Profile page
- [ ] **Remove a quiz**
- [ ] **Remove account**
- [ ] Change password

![](documentation/images/index.png)

![](documentation/images/create-quiz.png)

![](documentation/images/take-quiz.png)

![](documentation/images/quiz-stats.png)

## Database Tables
| Name | Data |
| - | - |
| Users | user_id SERIAL PRIMARY KEY, username TEXT, password TEXT, admin BOOL |
| Quizzes | quiz_id SERIAL PRIMARY KEY, creator_id INTEGER, title TEXT,  date TIMESTAMP, upvotes INTEGER, downvotes INTEGER |
| Questions | question_id SERIAL PRIMARY KEY, quiz_id INTEGER, question TEXT |
| Answers | answer_id SERIAL PRIMARY KEY, question_id INTEGER, answer TEXT, correct BOOL |
| Comments | comment_id SERIAL PRIMARY KEY, quiz_id INTEGER, user_id INTEGER, message TEXT, date TIMESTAMP |
| Scores | user_id INTEGER, quiz_id INTEGER, score INTEGER
| Log | log_id SERIAL PRIMARY KEY, date TIMESTAMP, user_id INTEGER, action TEXT

![](documentation/images/database_chart.png)