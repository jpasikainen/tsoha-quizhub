# Quizhub
Database project built with Flask and PostgreSQL for hy-tsoha.

## Description
- Generic social media like feed where posts are quizzes
- A quiz consists of multiple questions and answers to choose from
- After the quiz is over, the user can comment, rate the quiz, and is rewarded points based on their speed and accuracy
- All the users can create and take part in quizzes
- Admins can remove quizzes, users, and comments

## Views
**Bolded** tasks are main features.

### Feed (index.html)
- [ ] **Display quizzes in creation order**
- [ ] **Open the quiz on click**
- [ ] **Create a quiz button**
- [ ] Add sorting
- [ ] Add search

### Quiz (quiz/\<int>.html)
- [ ] **Opens to a new page**
- [ ] **Display a question and multiple choices**
- [ ] **Add a timer**
- [ ] **Reward points after completion**
- [ ] **Rate the quiz**
- [ ] **Add comments**
- [ ] **An admin can remove the quiz**
- [ ] Correct/Incorrect answers per question (statistics)

### Create user (register.html)
- [ ] **Form with username and password fields**
- [ ] **On submit check if the username is taken**
- [ ] **Hash the password before saving**

### Login (login.html)
- [ ] **Form with username and password fields**
- [ ] **On submit check if the password hash is correct and login**

### Create quiz (create.html)
- [ ] **Quiz name**
- [ ] **Add question and up to 4 answers choices**
- [ ] **Ability add multiple questions**
- [ ] Save draft
- [ ] Add tags
- [ ] Human verification before publishing

### Profile page (profile/\<int>.html)
- [ ] **Remove a quiz**
- [ ] **Remove account**
- [ ] Change password

![](documentation/images/index.png)

![](documentation/images/create-quiz.png)

![](documentation/images/take-quiz.png)

![](documentation/images/quiz-stats.png)

## Database

[Schema](https://github.com/jpasikainen/tsoha-quizhub/blob/master/schema.sql)

- [ ] Add bool published for quizzes 

![](documentation/images/database_chart.png)