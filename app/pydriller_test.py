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
    repo_path = os.path.join("repositories", repo_url.split('/')[-2])  # Create directory for the repository
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)

    for commit in Repository(repo_url).traverse_commits():
        if commit.hash == commit_hash:
            diffs = []
            for modification in commit.modifications:
                diffs.append(
                    {'src_code_before': modification.source_code_before, 'src_code_after': modification.source_code})
            return diffs

    return []


def link_exists_in_database(cursor, link):
    cursor.execute('SELECT COUNT(*) FROM urls WHERE url = %s', (link,))
    count = cursor.fetchone()[0]
    return count > 0


def search_and_store_links(root_folder):
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        user='root',
        password='password',
        database='db_commits'
    )
    cursor = conn.cursor()

    for root, dirs, files in os.walk(root_folder):
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
                                github_commit_references = find_github_commit_references(url)
                                if github_commit_references:
                                    print(f"Found in {file_path}: {url}")

                                    for commit_url in github_commit_references:
                                        commit_hash = commit_url.split('/')[-1]
                                        repo_url = extract_repo_url(commit_url)
                                        diffs = fetch_diff_of_commit(repo_url, commit_hash)

                                        for diff in diffs:
                                            # Check if link already exists in database
                                            if not link_exists_in_database(cursor, url):
                                                # Insert link, repo name, and CVE file path into database
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

                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in {file_path}: {e}")

                    except Exception as ex:
                        print(f"An error occurred: {ex}")

    cursor.close()
    conn.close()


# Example usage
base_folder = 'C:/Users/Rojhat - main/PycharmProjects/bachelor-project/data'
cve_folder = os.path.join(base_folder, 'cves')

search_and_store_links(cve_folder)
