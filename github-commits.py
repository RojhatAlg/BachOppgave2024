from pydriller import Repository

for commit in Repository('https://github.com/RojhatAlg/00-welcome-to-cloud9').traverse_commits():
    print('Hash {}, author {}'.format(commit.hash, commit.author.name))
