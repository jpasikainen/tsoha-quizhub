This is the initial design document for the project. There will be no further updates.

## Views
**Bolded** tasks are main features.

### Feed (index.html)
- [x] **Display quizzes in creation order**
- [x] **Open the quiz on click**
- [x] **Create a quiz button**
- [ ] Add sorting
- [ ] Add search

### Quiz (quiz/\<int>.html)
- [x] **Opens to a new page**
- [x] **Display a question and multiple choices**
- [x] **Reward points after completion**
- [x] **Rate the quiz**
- [x] **An admin can remove the quiz**
- [x] Correct/Incorrect answers per question (statistics)
- [ ] Add comments

### Create user (register.html)
- [x] **Form with username and password fields**
- [x] **On submit check if the username is taken**
- [x] **Hash the password before saving**

### Login (login.html)
- [x] **Form with username and password fields**
- [x] **On submit check if the password hash is correct and login**

### Create quiz (create.html)
- [x] **Quiz name**
- [x] **Add question and up to 4 answers choices**
- [x] **Ability add multiple questions**
- [ ] Save draft
- [ ] Add tags
- [ ] Human verification before publishing

### Profile page (profile/\<int>.html)
- [x] **Remove a quiz**
- [x] **Remove account**
- [x] **Edit a quiz**
- [ ] Change password

![](./images/index.png)

![](./images/create-quiz.png)

![](./images/take-quiz.png)

![](./images/quiz-stats.png)

## Database

[Schema](https://github.com/jpasikainen/tsoha-quizhub/blob/master/schema.sql)

- [x] Add bool published for quizzes 

![](documentation/images/database_chart.png)