import json
import os
import time
import logging
import subprocess
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load tasks from JSON file
def load_tasks(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("config.json not found!")
        return []
    except json.JSONDecodeError:
        logging.error("Invalid JSON format in config.json!")
        return []

# Write code to the specified file
def push_code(task):
    try:
        os.makedirs(os.path.dirname(task['file']), exist_ok=True)

        with open(task['file'], 'w') as f:
            f.write(task['code'])

        logging.info(f"Code successfully written to {task['file']}")

        # Commit & Push the code
        commit_and_push(task)
    except Exception as e:
        logging.error(f"Error writing code to {task['file']}: {e}")


def commit_and_push(task):
    try:
        # Pull latest changes before making any commit (avoids push failures)
        subprocess.run(["git", "pull", "origin", task["branch"], "--rebase", "--autostash"], check=True)

        # Stage ALL changes, including deletions
        subprocess.run(["git", "add", "--all"], check=True)

        # Commit changes with the provided message
        subprocess.run(["git", "commit", "-m", task["commit_message"]], check=True)

        # Push to the specified branch
        subprocess.run(["git", "push", "origin", task["branch"]], check=True)

        logging.info(f"✅ Changes successfully pushed to {task['branch']} branch.")
    
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Git error: {e}")


# Determine if it's time to execute a task
def should_run_task(task):
    return datetime.now() >= datetime.fromisoformat(task['time'])

# Handle repeat tasks
def update_task_time(task):
    if task["repeat"] == "daily":
        task["time"] = (datetime.fromisoformat(task["time"]) + timedelta(days=1)).isoformat()
    elif task["repeat"] == "weekly":
        task["time"] = (datetime.fromisoformat(task["time"]) + timedelta(weeks=1)).isoformat()

# Find next execution time
def get_next_execution_time(tasks):
    upcoming_tasks = [datetime.fromisoformat(task['time']) for task in tasks if datetime.fromisoformat(task['time']) > datetime.now()]
    return min(upcoming_tasks) if upcoming_tasks else None

# Main execution loop
def main():
    tasks = load_tasks(r'D:\test\jsonauto\config.json')
    executed_tasks = set()  # Prevent duplicate execution

    while tasks:
        for task in tasks[:]:
            if should_run_task(task) and task["id"] not in executed_tasks:
                push_code(task)
                executed_tasks.add(task["id"])

                if task["repeat"] != "none":
                    update_task_time(task)  # Reschedule task
                else:
                    tasks.remove(task)  # Remove non-repeating tasks

        next_time = get_next_execution_time(tasks)
        if next_time:
            sleep_time = (next_time - datetime.now()).total_seconds()
            logging.info(f"Next execution in {sleep_time:.2f} seconds.")
            time.sleep(max(sleep_time, 1))
        else:
            break  # No more tasks to execute

if __name__ == "__main__":
    main()
