from pydriller import Repository

for commit in Repository('https://github.com/amazon-ion/ion-java').traverse_commits():
    print('Hash {}, author {}'.format(commit.hash, commit.author.name))
