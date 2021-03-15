CREATE TABLE users (
    id SERIAL PRIAMRY KEY,
    username TEXT UNIQUE,
    password TEXT,
    admin BOOL
);

CREATE TABLE quizzes (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER REFERENCES users,
    title TEXT,
    date TIMESTAMP,
    published BOOL,
    upvotes INTEGER,
    downvotes INTEGER
);

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quizzes,
    question TEXT
);

CREATE TABLE answers (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES questions,
    answer TEXT,
    correct BOOL
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quizzes,
    user_id INTEGER REFERENCES users,
    message TEXT,
    date TIMESTAMP
);

CREATE TABLE scores (
    user_id INTEGER REFERENCES users,
    quiz_id INTEGER REFERENCES quizzes,
    score INTEGER
);

CREATE TABLE log (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP,
    user_id INTEGER,
    action TEXT
);