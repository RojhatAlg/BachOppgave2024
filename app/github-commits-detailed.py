import os
from pydriller import Repository
import mysql.connector

# Connect to MySQL database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'db_commits',
}
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Fetch URLs from the database
select_query = "SELECT url FROM urls"
cursor.execute(select_query)
urls = cursor.fetchall()

# Process each URL
for url in urls:
    repo_url = url[0]  # Extract the URL from the tuple

    # Define the path to the temp_repo directory
    temp_repo_path = '../data/temp_repo'

    # Check if temp_repo directory exists, if not, create it
    if not os.path.exists(temp_repo_path):
        os.makedirs(temp_repo_path)

    # Clone the repository to the temp_repo directory
    repo = Repository(repo_url, clone_repo_to=temp_repo_path)

    # Iterate over all commits
    for commit in repo.traverse_commits():
        print('Commit Hash: {}, Author: {}'.format(commit.hash, commit.author.name))
        print('Message: {}'.format(commit.msg))
        # Process other details of the commit as needed

cursor.close()
conn.close()
