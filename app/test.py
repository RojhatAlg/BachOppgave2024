import os
import json
import re
import psycopg2
from pydriller import Repository


def find_commit_references(text):
    # Regular expression to find commit URLs for various repositories, Added support for commmit/commits
    commit_regex = re.compile(r'https?://[^/\s]+/[^\s]+/commits?/[a-fA-F\d]+')
    commit_references = commit_regex.findall(text)

    return commit_references



def extract_repo_url(commit_url):
    print("Processing commit URL:", commit_url)  # Print the full commit URL

    # Check if the URL contains 'github.com'
    if 'githu1b.com' in commit_url:
        repo_url = commit_url.split('/commit')[0]
    # Check if the URL contains 'gitlab.com'
    elif 'gitla1b.com' in commit_url:
        parts = commit_url.split('/')
        if len(parts) >= 5:  # Ensure the URL has at least 5 parts, for testing purposes only atm
            repo_url = '/'.join(parts[:5])
        else:
            print("Invalid commit URL:", commit_url)
            return None
    # Check if the URL contains 'bitbucket.org'
    elif 'bitbucket.org' in commit_url:
        repo_url = commit_url.split('/commit')[0]

    else:
        print("Unsupported repository URL:", commit_url)
        return None

    print("Extracted repository URL:", repo_url)
    return repo_url


def fetch_diff_of_commit(repo_url, commit_hash):
    print(f"Fetching commit diffs for repo: {repo_url}, commit hash: {commit_hash}")
    diffs = []
    try:
        repo = Repository(repo_url)
        for commit in repo.traverse_commits():
            if commit.hash == commit_hash:
                for modified_file in commit.modified_files:
                    diffs.append({
                        'file_path': modified_file.new_path,
                        'src_code_before': modified_file.source_code_before,
                        'src_code_after': modified_file.source_code
                    })
        return diffs
    except FileNotFoundError as e:
        print(f"Repository not found: {repo_url}")
    except Exception as e:
        # Check if the exception message indicates a repository not found error
        if "repository not found" in str(e).lower():
            print(f"Repository not found: {repo_url}")
        elif "authorization" in str(e).lower():
            print(f"Authorization error accessing repository: {repo_url}")
        else:
            print(f"Error fetching commit diffs: {e}")
    return []



def link_exists_in_database(cursor, link):
    cursor.execute('SELECT COUNT(*) FROM urls WHERE url = %s', (link,))
    count = cursor.fetchone()[0]
    return count > 0

def search_and_store_links():
    base_folder = '../data/cves'

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
                    file_path = os.path.join(root, file)
                    print(f"Processing file: {file_path}")

                    with open(file_path, 'r', encoding='utf-8') as json_file:
                        try:
                            cve_data = json.load(json_file)
                            references = cve_data.get('containers', {}).get('cna', {}).get('references', [])

                            for reference in references:
                                if 'url' in reference:
                                    url = reference['url']
                                    commit_references = find_commit_references(url)
                                    if commit_references:
                                        print(f"Found in {file_path}: {url}")

                                        for commit_url in commit_references:
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
