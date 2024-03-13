CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    repo_name TEXT NOT NULL,
    cve_file_path TEXT NOT NULL,
    src_code_before TEXT NOT NULL,
    src_code_after TEXT NOT NULL
);
