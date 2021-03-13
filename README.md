# Quizhub
Database project built with Flask and PostgreSQL for hy-tsoha.

## Description
- Twitter like feed where posts are quizes
- A quiz consists of questions and multiple answers to choose from
- After the quiz is over, the user can rate the quiz and is rewarded points based on the speed and accuracy
- All the users can create and take part in quizes
- Admins can remove quizes and users

## Views
**Bolded** tasks are main features.

### Feed
- [ ] **Display quizes in creation order**
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

## Database Tables
| Name | Data |
| - | - |
| Users | id SERIAL PRIMARY KEY, username TEXT, password TEXT, points NUMBER, admin BOOL |
| Quizes | id SERIAL PRIMARY KEY, creator_id INTEGER, title TEXT, question_ids INTEGER ARRAY, date TIMESTAMP, upvotes INTEGER, downvotes INTEGER |
| Questions | id SERIAL PRIMARY KEY, question TEXT, correct BOOL |
| Comments | id SERIAL PRIMARY KEY, quiz_id INTEGER, user_id INTEGER, message TEXT, creation date TIMESTAMP |
| Scores | id SERIAL PRIMARY KEY, user_id INTEGER, score INTEGER
| Log | id SERIAL PRIMARY KEY, user_id INTEGER, action TEXT