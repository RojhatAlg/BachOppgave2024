# Github workflow 
Follow these steps to create a new branch, make changes, and push them to GitHub using Git:

# Step 1: create a new branch named 'example'
git branch example

# Step 2: switch to the newly created branch
git checkout example

# Step 3: verify that you are on the correct branch
git branch



# Step 4: stage changes
git add .

# Step 5: Commit changes with a descriptive message
git commit -m "Added work"

# Step 6: Push the branch to GitHub and set it as the upstream branch
git push --set-upstream origin example

# Step 7: Create a Merge Request on GitHub Open your browser and go to the GitHub repository. 
Click on the "Pull Requests" tab. Click the "New Pull Request" button. 
Choose the base branch (e.g., "main") and the compare branch (e.g., "example"). 
Add a descriptive title and description for your changes. 
Click the "Create Pull Request" button.

# Step 8: 
Merge the Pull Request Review the changes in the pull request. 
If everything looks good, click the "Merge Pull Request" button. 
Optionally, add a comment and confirm the merge.
