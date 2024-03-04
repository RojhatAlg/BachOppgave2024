import os
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

    # Print the URL for verification
    print("Original URL:", repo_url)

    # Check if the URL is a valid GitHub repository URL
    if "github.com" in repo_url:
        print("This is a valid GitHub repository URL.")
    else:
        print("This URL does not belong to a GitHub repository.")
        # Optionally, you can correct or ignore invalid URLs here

cursor.close()
conn.close()
