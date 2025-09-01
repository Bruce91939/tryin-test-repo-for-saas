import json
import subprocess
import os
import base64
from datetime import datetime

# Auto-generated files that should be ignored unless modified
IGNORED_FILES = [
    "node_modules/", "package-lock.json", "requirements.txt",
    "build/", "dist/", ".gitignore"
]

# Important system-managed files that should still be tracked if changed
TRACKED_SYSTEM_FILES = [
    "Dockerfile", ".env", "config/", ".github/workflows/"
]

def get_commit_history(repo_path):
    """Retrieve commit history from the given repo."""
    commits = subprocess.check_output([
        "git", "-C", repo_path, "log", "--pretty=format:%H|%ad|%s", "--date=iso"
    ]).decode("utf-8").splitlines()
    
    commit_data = []
    for commit in commits:
        parts = commit.split("|")
        commit_data.append({
            "hash": parts[0],
            "date": parts[1],
            "message": parts[2]
        })
    return commit_data

def get_commit_files(repo_path, commit_hash):
    """Get list of files changed in a commit."""
    files = subprocess.check_output([
        "git", "-C", repo_path, "show", "--pretty=format:", "--name-only", commit_hash
    ]).decode("utf-8").strip().split("\n")
    
    return [file for file in files if file and (file.startswith(tuple(TRACKED_SYSTEM_FILES)) or not file.startswith(tuple(IGNORED_FILES)))]

def is_binary_file(repo_path, commit_hash, file_path):
    """Check if a file is binary."""
    try:
        output = subprocess.run(
            ["git", "show", f"{commit_hash}:{file_path}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            errors="ignore"
        )
        return "\0" in output.stdout  # If null bytes exist, it's binary
    except subprocess.CalledProcessError:
        return True  # Assume binary if we can't read it

def get_file_diff(repo_path, commit_hash, file_path):
    """Retrieve only the changed lines (diff) of a file in a commit."""
    try:
        diff_output = subprocess.run(
            ["git", "-C", repo_path, "diff", f"{commit_hash}^!", "--", file_path],
            capture_output=True,
            text=True,
            errors="ignore"
        ).stdout
        return diff_output.strip()
    except subprocess.CalledProcessError:
        return ""

def get_file_content(repo_path, commit_hash, file_path):
    """Retrieve file content or base64 encode binary files."""
    try:
        if is_binary_file(repo_path, commit_hash, file_path):
            binary_data = subprocess.run(
                ["git", "show", f"{commit_hash}:{file_path}"],
                cwd=repo_path,
                capture_output=True
            ).stdout
            return base64.b64encode(binary_data).decode("utf-8")  # Convert to base64

        # Read text file content
        return subprocess.run(
            ["git", "show", f"{commit_hash}:{file_path}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            errors="ignore"
        ).stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def get_branch_name(repo_path):
    """Retrieve the current branch name of the repository."""
    return subprocess.check_output(["git", "-C", repo_path, "branch", "--show-current"]).decode("utf-8").strip()

def generate_json(repo_path):
    """Generate JSON structure from commit history."""
    commits = get_commit_history(repo_path)
    output = []
    id_counter = 1
    branch = get_branch_name(repo_path)

    for commit in commits:
        commit_hash = commit["hash"]
        commit_time = datetime.fromisoformat(commit["date"]).strftime("%Y-%m-%dT%H:%M:%S")
        files = get_commit_files(repo_path, commit_hash)

        for file in files:
            file_diff = get_file_diff(repo_path, commit_hash, file)
            if is_binary_file(repo_path, commit_hash, file):
                file_diff = f"<base64-encoded-data>"

            # Handle Auto-generated files differently
            if file.startswith(tuple(IGNORED_FILES)):
                if file_diff:
                    output.append({
                        "id": id_counter,
                        "file": file,
                        "code": file_diff,
                        "time": commit_time,
                        "commit_message": commit["message"],
                        "branch": branch,
                        "repeat": "none"
                    })
                else:
                    output.append({
                        "id": id_counter,
                        "file": file,
                        "status": "Pushed but auto-generated"
                    })
            else:
                output.append({
                    "id": id_counter,
                    "file": file,
                    "code": file_diff if file_diff else "[No manual changes]",
                    "time": commit_time,
                    "commit_message": commit["message"],
                    "branch": branch,
                    "repeat": "none"
                })
            id_counter += 1

    return output

if __name__ == "__main__":
    repo_path = input("Enter the path to your Git repository: ").strip()
    
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        print("❌ Error: Not a valid Git repository!")
    else:
        result = generate_json(repo_path)
        output_file = os.path.join(repo_path, "commit_history.json")
        
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ commit_history.json has been generated at: {output_file}")
