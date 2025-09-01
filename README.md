after coping the folder in the codespace
🚀 Full Workflow: Import Repo as Subtree + Fix Author Email + Push
1. Start fresh — clean any old folders
rm -rf test-repo-for-saas

2. Add the external repo as a remote
git remote add saas-repo https://github.com/SAMEER-40/test-repo-for-saas.git

3. Fetch the remote
git fetch saas-repo

4. Merge with subtree strategy, allowing unrelated histories
git merge -s ours --allow-unrelated-histories --no-commit saas-repo/main

5. Read the tree into a subfolder
git read-tree --prefix=test-repo-for-saas/ -u saas-repo/main

6. Commit the merge
git commit -m "Imported test-repo-for-saas with full history"

7. Remove the temporary remote
git remote remove saas-repo

8. Check all unique author emails in imported commits
git log -- test-repo-for-saas/ --pretty=format:"%an <%ae>" | sort | uniq

9. Replace the old email(s) with your GitHub email

Find your GitHub email here: https://github.com/settings/emails

Example: 168720864+Bruce91939@users.noreply.github.com

Use the following command, replacing the example old email(s) and your info:

git filter-branch --env-filter '
OLD_EMAIL="old@example.com"
CORRECT_NAME="Your Name"
CORRECT_EMAIL="yourgithubemail@users.noreply.github.com"

if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]; then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]; then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
' -- --all


Repeat the if block for each old email if needed.

10. Force push your rewritten history
git push --force origin main

11. Verify commits and contribution graph

Run:

git log -- test-repo-for-saas/ --pretty=format:"%h %an <%ae>"


Wait ~minutes to hours for GitHub to update your contribution graph.
