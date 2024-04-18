import os
import json
import re
import psycopg2
import threading
from pydriller import Repository


def find_commit_references(text):
    # Regular expression to find commit URLs for various repositories, Added support for commmit/commits
    commit_regex = re.compile(r'https?://[^/\s]+/[^\s]+/commits?/[a-fA-F\d]+')
    commit_references = commit_regex.findall(text)

    return commit_references

def extract_repo_url(commit_url):
    print("Processing commit URL:", commit_url)  # Print the full commit URL

    # Dictionary mapping repository domains to their URL parsing functions
    repo_parsing_functions = {
        "git.kernel.org": lambda url: '/'.join(url.split('/')[:7]),
        "gitee.com": lambda url: url.split('/commit')[0],
        "github.com": lambda url: url.split('/commit')[0],
        "bitbucket.org": lambda url: url.split('/commit')[0],
        "gitlab.com": lambda url: '/'.join(url.split('/')[:5]) if 'gitlab.com' in url else url.split('/commit')[0],
        "gitweb.torproject.org": lambda url: '/'.join(url.split('/')[:5]),
        "git.sr.ht": lambda url: url.split('/commit')[0],
        "gitlab.manjaro.org": lambda url: '/'.join(url.split('/')[:5]),
        "gitlab.xfce.org": lambda url: '/'.join(url.split('/')[:5]),
        "git.imagemagick.org": lambda url: url.split('/commit')[0],
        "git.freepbx.org": lambda url: url.split('/commit')[0],
        "framagit.org": lambda url: url.split('/commit')[0],
        "freeswitch.org": lambda url: url.split('/commit')[0],
        "git.process-one.net": lambda url: url.split('/commit')[0],
        "source.winehq.org": lambda url: url.split('/commit')[0],
        "lab.louiz.org": lambda url: url.split('/commit')[0],
        "opendev.org": lambda url: url.split('/commit')[0],
        "git.magnolia-cms.com": lambda url: url.split('/commit')[0],
        "code.videolan.org": lambda url: url.split('/commit')[0],
        "git.pengutronix.de": lambda url: url.split('/commit')[0],
        "gitlab.freedesktop.org": lambda url: url.split('/commit')[0],
        "git.enlightenment.org": lambda url: url.split('/commit')[0],
        "git.drupalcode.org": lambda url: url.split('/commit')[0],
        "git.launchpad.net": lambda url: url.split('/commit')[0],
        "src.openvz.org": lambda url: url.split('/commit')[0],
        "www.codeaurora.org": lambda url: url.split('/commit')[0],
        "0xacab.org": lambda url: url.split('/commit')[0],
        "code.vtiger.com": lambda url: url.split('/commit')[0],
        "git.tt-rss.org": lambda url: url.split('/commit')[0],
        "gitlab.labs.nic.cz": lambda url: url.split('/commit')[0],
        "stash.kopano.io": lambda url: url.split('/commit')[0],
        "git.bluemind.net": lambda url: url.split('/commit')[0],
        "git.exim.org": lambda url: url.split('/commit')[0],
        "git.spip.net": lambda url: url.split('/commit')[0],
        "git.ffmpeg.org": lambda url: url.split('/commit')[0],
        "git.lysator.liu.se": lambda url: url.split('/commit')[0],
        "dev.gajim.org": lambda url: url.split('/commit')[0],
        "invent.kde.org": lambda url: url.split('/commit')[0],
        "source.denx.de": lambda url: url.split('/commit')[0],
        "gitea.treehouse.systems": lambda url: url.split('/commit')[0],
        "gitlab.gnome.org": lambda url: url.split('/commit')[0],
        "gitlab.marlam.de": lambda url: url.split('/commit')[0],
        "gitlab.matrix.org": lambda url: url.split('/commit')[0],
        "qt.gitorious.org": lambda url: '/'.join(url.split('/')[:6])
    }

    # Check if the URL contains any of the valid repository domains
    for domain, parse_function in repo_parsing_functions.items():
        if domain in commit_url:
            repo_url = parse_function(commit_url)
            print("Extracted repository URL:", repo_url)
            return repo_url

    # If the URL doesn't match any of the known repository domains
    print("Unsupported repository URL:", commit_url)
    return None


def fetch_diff_of_commit(repo_url, commit_hash):
    diffs = []
    timeout = 60  # Timeout set to 60 seconds

    def fetch_commit_diffs_thread():
        nonlocal diffs
        try:
            for commit in Repository(repo_url).traverse_commits():
                if commit.hash == commit_hash:
                    for modified_file in commit.modified_files:
                        diffs.append({
                            'file_path': modified_file.new_path,
                            'src_code_before': modified_file.source_code_before,
                            'src_code_after': modified_file.source_code
                        })
        except Exception as e:
            print(f"Error fetching commit diffs: {e}")

    thread = threading.Thread(target=fetch_commit_diffs_thread)
    thread.start()
    thread.join(timeout)  # Wait for the thread to complete or timeout

    if thread.is_alive():
        print("Fetching commit diffs timed out. Skipping to next commit...")
        return []

    return diffs

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
                            conn.rollback()
                            print(f"An error occurred: {ex}")

        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")

# Example usage
search_and_store_links()
