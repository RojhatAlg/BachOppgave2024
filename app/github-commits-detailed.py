import os
import json
import re
import psycopg2
from pydriller import Repository

def find_github_commit_references(text):
    commit_regex = re.compile(r'https://github\.com/[^/]+/[^/]+/commit/[a-fA-F\d]+')
    # Find all GitHub commit URLs in the text using REGEX
    github_commit_references = re.findall(commit_regex, text)
    return github_commit_references

def extract_repo_url(commit_url):
    # Remove everything after the last forward slash (/)
    repo_url = commit_url.rsplit('/', 2)[0]
    return repo_url

def fetch_diff_of_commit(repo_url, commit_hash):
    diffs = []
    try:
        repo = Repository(repo_url)
        for commit in repo.traverse_commits():
            if commit.hash == commit_hash:
                for modified_file in commit.modified_files:
                    diffs.append(
                        {'file_path': modified_file.new_path,
                         'src_code_before': modified_file.source_code_before,
                         'src_code_after': modified_file.source_code})
        return diffs
    except Exception as e:
        print(f"Error fetching commit diffs: {e}")
        return []

def link_exists_in_database(cursor, link):
    cursor.execute('SELECT COUNT(*) FROM urls WHERE url = %s', (link,))
    count = cursor.fetchone()[0]
    return count > 0

def search_and_store_links():
    # Get the directory of the current Python script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Define the root folder
    base_folder = os.path.join(script_dir, '..', 'data', 'cves')

    # Connect to PostgreSQL database
    try:
        conn = psycopg2.connect(
            user='root',
            password='password',
            database='db_commits'
        )
        cursor = conn.cursor()

        for root, dirs, files in os.walk(base_folder):
            for file in files:
                if file.endswith('.json') and file.startswith('CVE-'):
                    file_path = os.path.relpath(os.path.join(root, file), base_folder)  # Get the relative file path
                    print(f"Processing file: {file_path}")

                    with open(os.path.join(root, file), 'r', encoding='utf-8') as json_file:
                        try:
                            cve_data = json.load(json_file)
                            references = cve_data.get('containers', {}).get('cna', {}).get('references', [])

                            for reference in references:
                                if 'url' in reference:
                                    url = reference['url']
                                    github_commit_references = find_github_commit_references(url)
                                    if github_commit_references:
                                        print(f"Found in {file_path}: {url}")

                                        for commit_url in github_commit_references:
                                            commit_hash = commit_url.split('/')[-1]
                                            repo_url = extract_repo_url(commit_url)

                                            diffs = fetch_diff_of_commit(repo_url, commit_hash)

                                            for diff in diffs:
                                                print("Inserting diff into database:", diff)

                                                if not link_exists_in_database(cursor, url):
                                                    print("Link not found in database. Inserting...")

                                                    try:
                                                        cursor.execute(
                                                            'INSERT INTO urls (url, repo_name, cve_file_path, src_code_before, src_code_after) VALUES (%s, %s, %s, %s, %s)',
                                                            (url, repo_url, file_path, diff['src_code_before'],
                                                             diff['src_code_after']))
                                                        conn.commit()

                                                        print("New row added to database:")
                                                        print("URL:", url)
                                                        print("Repo Name:", repo_url)
                                                        print("CVE File Path:", file_path)
                                                        print("Src Code Before:", diff['src_code_before'])
                                                        print("Src Code After:", diff['src_code_after'])
                                                    except psycopg2.Error as err:
                                                        conn.rollback()  # Rollback the transaction
                                                        print("PostgreSQL Error:", err)
                                                    except Exception as ex:
                                                        conn.rollback()  # Rollback the transaction
                                                        print("An error occurred during insertion:", ex)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON in {file_path}: {e}")
                        except Exception as ex:
                            conn.rollback()  # Rollback the transaction
                            print(f"An error occurred: {ex}")

        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")

# Example usage
search_and_store_links()
