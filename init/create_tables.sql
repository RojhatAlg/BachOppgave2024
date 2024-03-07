CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    url VARCHAR(2048) NOT NULL,
    repo_name VARCHAR(2048) NOT NULL,
    cve_file_path VARCHAR(2048) NOT NULL,
    src_code_before VARCHAR(32768) NOT NULL,
    src_code_after VARCHAR(32768) NOT NULL
);
