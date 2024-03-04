# Test fetching and storing commits to database.

from pydriller import Repository
import mysql.connector



db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'db_commits',
}

# Establish MySQL connection
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Repository URL
repo_url = 'https://github.com/amazon-ion/ion-java'

for commit in Repository(repo_url).traverse_commits():
    commit_hash = commit.hash
    author_name = commit.author.name

    insert_query = "INSERT INTO commits (hash, author_name) VALUES (%s, %s)"
    values = (commit_hash, author_name)

    try:
        cursor.execute(insert_query, values)
        conn.commit()
        print(f"Commit {commit_hash} by {author_name} successfully inserted into the database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Close MySQL connection
cursor.close()
conn.close()