import os
import time
import random
import git
import shutil
from datetime import datetime, timedelta

# Configuration
SOURCE_REPO = "https://github.com/bradtraversy/50projects50days.git"
DESTINATION_REPO = "https://github.com/SAMEER-40/test-repo-for-saas.git"
LOCAL_DIR = "D:\\test\\automategithub"

def clone_repo(source_url, local_dir):
    """Clones a GitHub repository to a local directory or pulls updates if it exists."""
    if not os.path.exists(local_dir) or not os.path.isdir(os.path.join(local_dir, ".git")):
        if os.path.exists(local_dir):
            print("⚠️ Found an invalid Git directory. Deleting and re-cloning...")
            shutil.rmtree(local_dir)  # Remove invalid directory

        print(f"📥 Cloning repo from {source_url} to {local_dir} ...")
        repo = git.Repo.clone_from(source_url, local_dir, branch='master')
    else:
        print("🔄 Repo already exists. Fetching latest updates...")
        repo = git.Repo(local_dir)
        repo.remotes.origin.pull()  # Ensure the latest commits are pulled

    return repo


def replay_commits(source_repo, dest_repo_path):
    """Recreates commits from source repo in destination repo."""
    default_branch = source_repo.active_branch.name  # Get the actual branch name
    commits = list(source_repo.iter_commits(default_branch))[::-1]
    dest_repo = git.Repo.init(dest_repo_path)
    
    # Configure remote repo
    origin = dest_repo.create_remote('origin', DESTINATION_REPO) if 'origin' not in dest_repo.remotes else dest_repo.remotes['origin']

    if not commits:
        print("No commits found in source repository.")
        return

    # Copy commits one by one
    for commit in commits:
        new_time = commit.committed_datetime + timedelta(minutes=random.randint(1, 30))  # Randomize time
        new_time_str = new_time.strftime('%Y-%m-%dT%H:%M:%S')

        # Checkout and apply changes
# Check if 'main' branch exists
    if 'main' in dest_repo.heads:
        dest_repo.git.checkout('main')  # Switch to the existing main branch
    else:
        dest_repo.git.checkout('-b', 'main')  # Create and switch if it doesn't exist
        dest_repo.git.reset('--hard')  # Clear previous commits
        for file in commit.tree.traverse():
            if file.type == 'blob':  # Only process files, not directories
                file_path = os.path.join(dest_repo_path, file.path)
                with open(file_path, "wb") as f:
                    f.write(file.data_stream.read())  # Save file

    dest_repo.git.add(A=True)
    dest_repo.index.commit(commit.message, author=commit.author, author_date=new_time_str, commit_date=new_time_str)
    print(f"Committed: {commit.message.strip()} at {new_time}")

    # Push all commits to new repo
    dest_repo.git.push('origin', 'main', '--force')

    print("All commits pushed successfully.")

def automate_push():
    source_repo = clone_repo(SOURCE_REPO, LOCAL_DIR)
    replay_commits(source_repo, LOCAL_DIR)

if __name__ == "__main__":
    while True:
        automate_push()
        sleep_time = random.randint(0)  # Random interval between 1 hour and 1 day
        print(f"Next push in {sleep_time} seconds...")
        time.sleep(sleep_time)