CREATE TABLE grades (
    id SERIAL PRIMARY KEY,
    exam_date DATE NOT NULL,
    group_name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    grade INTEGER NOT NULL CHECK (grade BETWEEN 2 AND 5)
);