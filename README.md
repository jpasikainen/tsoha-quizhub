# Quizhub
Database project built with Flask and PostgreSQL for [hy-tsoha](https://hy-tsoha.github.io/materiaali/index).

Deployed to heroku at https://tsoha-quizhub.herokuapp.com/ . Login by pressing "Login/Register" button at top right corner. Use the existing accounts marked below or create a new one. After logging in you are redirected to the main page and can now play the quizzes or create one yourself.

When entering a quiz, click one of the options to progress. After you have gone through all the questions, you will see the results.

When creating a new quiz, input a quiz title, questions, and at least one answer for each question. The last question can be removed by pressing "Remove Last Question". After you're finished, press "Publish". Publishing a makes it visible to all the users.

By clicking on your name, you enter a profile view. There you can delete your account, remove a quiz, or edit one. Deleting the account doesn't remove quizzes, but hides them. The quizzes can still be accessed via links.

Existing accounts:
| username | password | admin |
| - | - | - |
| user | password | False |
| admin | password | True |

## Description
- Generic social media like feed where posts are quizzes
- A quiz consists of multiple questions and answers to choose from
- After the quiz is over, the user can rate the quiz and view global statistics for it
- All the users can create and take part in quizzes
- Admins can remove quizzes

## Security

The site is protected from SQL-injection, XSS and CSRF vulnerabilities. SQL queries take variables as parameters. XSS is taken care of by Flask's `render_template` and FlaskWTF does CSRF checking with `validate_on_submit()`. Account name is limited to `^([a-zA-Z0-9åäö _!.,+-]+)$` Regex, and title and question fields are limited to `^([a-zA-Z0-9åäö$€'" _!.,+-]+)$`.

## Design

The [Design Document](/documentation/design.md) contains the original plan for the project.