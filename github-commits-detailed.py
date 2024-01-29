import os

from pydriller import Repository

repo_url = 'https://github.com/RojhatAlg/00-welcome-to-cloud9'  # Replace with repo URL
commit_hash = 'c5f92472ecc412ec704de5ffcc4a06b58976875a'  # Replace with the specific commit hash you want to analyze

# Path to the temp_repo directory
temp_repo_path = 'temp_repo'

# Check if temp_repo directory exists
if not os.path.exists(temp_repo_path):
    # If it doesn't exist, create the new directory, if it exists do nothing
    os.makedirs(temp_repo_path)


# Clone the repository to the temp_repo directory
repo = Repository(repo_url, clone_repo_to='temp_repo')

# Iterate over all commits until commit hash is found
for commit in repo.traverse_commits():
    if commit.hash == commit_hash:
        print('Commit Hash: {}, Author: {}'.format(commit.hash, commit.author.name))
        print('Message: {}'.format(commit.msg))

        # Iterate over all modified files in the commit and print details
        for modified_file in commit.modified_files:
            print('\nFile: {}, Change Type: {}'.format(modified_file.filename, modified_file.change_type.name))
            print('Added Lines: {}, Deleted Lines: {}'.format(modified_file.added_lines, modified_file.deleted_lines))
            print('Complexity: {}'.format(modified_file.complexity))

            print('\nDiff:')
            print(modified_file.diff)

            print('\nSource Code Before:')
            print(modified_file.source_code_before)

            print('\nSource Code After:')
            print(modified_file.source_code)

        break  # Break out of the loop when commit hash is found
