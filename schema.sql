CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    admin BOOL DEFAULT FALSE
);

CREATE TABLE quizzes (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER REFERENCES users,
    title TEXT,
    date TIMESTAMP NOT NULL DEFAULT date_trunc('second', NOW()::TIMESTAMP),
    published BOOL DEFAULT FALSE,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    visible BOOL DEFAULT TRUE
);

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quizzes ON DELETE CASCADE,
    question TEXT
);

CREATE TABLE answers (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES questions ON DELETE CASCADE,
    answer TEXT,
    correct BOOL
);

CREATE TABLE user_answers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    quiz_id INTEGER REFERENCES quizzes ON DELETE CASCADE,
    answer_id INTEGER REFERENCES answers ON DELETE CASCADE,
    session_on BOOL DEFAULT TRUE
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quizzes,
    user_id INTEGER REFERENCES users,
    message TEXT,
    date TIMESTAMP NOT NULL DEFAULT date_trunc('second', NOW()::TIMESTAMP)
);

CREATE TABLE scores (
    user_id INTEGER REFERENCES users,
    quiz_id INTEGER REFERENCES quizzes ON DELETE CASCADE,
    score INTEGER
);

CREATE TABLE log (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL DEFAULT date_trunc('second', NOW()::TIMESTAMP),
    user_id INTEGER,
    action TEXT
);