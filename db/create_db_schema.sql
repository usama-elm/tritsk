CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    username VARCHAR(200) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    aftername VARCHAR(200),
    mail VARCHAR(200) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS priority (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) UNIQUE NOT NULL,
    rank SMALLINT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS status (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL
);

INSERT INTO status (title) VALUES ('to-do');
INSERT INTO status (title) VALUES ('doing');
INSERT INTO status (title) VALUES ('done');

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) UNIQUE NOT NULL,
    content TEXT,
    date_creation TIMESTAMP WITH TIME ZONE DEFAULT now(),
    priority_id BIGINT NOT NULL REFERENCES priority(id) ON UPDATE CASCADE ON DELETE NO ACTION,
    deadline DATE,
    state_id INTEGER NOT NULL FOREIGN KEY (state_id) REFERENCES status(id)
);

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS project_user_rel (
    id SERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    CONSTRAINT unique_user_project UNIQUE (user_id, project_id)
);

CREATE TABLE IF NOT EXISTS task_user_rel (
    task_id BIGINT NOT NULL REFERENCES tasks(id) ON UPDATE CASCADE ON DELETE CASCADE,
    project_id BIGINT REFERENCES projects(id) ON UPDATE CASCADE ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT unique_task_user_project UNIQUE (task_id, user_id, project_id)

);
