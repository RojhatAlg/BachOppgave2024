import os
import json
import re


def find_commit_references_in_cve_files(base_folder):
    commit_references = []

    # Regular expression to find commit URLs
    commit_regex = re.compile(r'https?://[^/\s]+/[^\s]+/commits?/[a-fA-F\d]+')

    try:
        for root, dirs, files in os.walk(base_folder):
            for file in files:
                if file.endswith('.json') and file.startswith('CVE-'):
                    file_path = os.path.join(root, file)
                    print(f"Processing file: {file_path}")  # Print current file being processed
                    with open(file_path, 'r', encoding='utf-8') as json_file:
                        try:
                            cve_data = json.load(json_file)
                            references = cve_data.get('containers', {}).get('cna', {}).get('references', [])

                            for reference in references:
                                if 'url' in reference:
                                    url = reference['url']
                                    commit_references.extend(commit_regex.findall(url))
                                    if commit_references:  # Check if commit_references is not empty
                                        print(
                                            f"Commit URLs found in {file}: {commit_references[-1]}")  # Print commit URLs found
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON in {file_path}: {e}")
                        except Exception as ex:
                            print(f"An error occurred: {ex}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return commit_references


if __name__ == "__main__":
    base_folder = '../data/cves'  # Update the folder path accordingly
    commit_urls = find_commit_references_in_cve_files(base_folder)
    repository_urls = set()

    # Extract repository domain names from commit URLs
    for url in commit_urls:
        domain = re.search(r'(https?://[^/\s]+)/', url)
        if domain:
            repository_urls.add(domain.group(1))

    print("Repository URLs found:")
    for repo_url in repository_urls:
        print(repo_url)
