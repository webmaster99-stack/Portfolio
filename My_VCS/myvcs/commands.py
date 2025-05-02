import os
import json
import time
import hashlib
import difflib

VCS_DIR = ".myvcs"
COMMITS_DIR = os.path.join(VCS_DIR, "commits")
INDEX_FILE = os.path.join(VCS_DIR, "index")
HEAD_FILE = os.path.join(VCS_DIR, "HEAD")


def init():
    os.makedirs(COMMITS_DIR,  exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        json.dump([], f)

    with open(HEAD_FILE, "w") as f:
        f.write("")

    print("Initialized empty VCS repository in .myvcs/")


def add(file_path):
    if not os.path.exists(file_path):
        print(f"{file_path} does not exist")
        return

    with open(INDEX_FILE, "r+") as f:
        try:
            staged = json.load(f)

        except json.JSONDecodeError:
            staged = []

        if file_path not in staged:
            staged.append(file_path)
            print(f"Added {file_path} to the staging area.")

        else:
            print(f"{file_path} is already staged")

        f.seek(0)
        json.dump(staged, f)
        f.truncate()


def remove(file_path):
    if not os.path.exists(INDEX_FILE):
        print("Repository not initialised.")
        return

    with open(INDEX_FILE, "r+") as f:
        staged = json.load(f)

        if file_path in staged:
            staged.remove(file_path)
            print(f"Removed {file_path} from the staging area")

        else:
            print(f"{file_path} was not staged")

        f.seek(0)
        json.dump(staged, f)
        f.truncate()


def commit(message):
    if not os.path.exists(INDEX_FILE):
        print("Repository not initialised")
        return

    with open(INDEX_FILE, "r+") as f:
        staged = json.load(f)

    if not staged:
        print("No files to commit")
        return

    commit_data = {
        "timestamp": time.time(),
        "message": message,
        "files": {},
        "parent": None
    }

    # Load HEAD (previous commit)
    if os.path.exists(HEAD_FILE):
        with open(HEAD_FILE, "r+") as f:
            parent = f.read().strip()
            if parent:
                commit_data["parent"] = parent

    # Save file contents
    for file in staged:
        if not os.path.exists(file):
            print(f"Warning: {file} not found. Skipping.")
            continue

        with open(file, "r", encoding="utf-8") as f:
            content= f.read()

        commit_data["files"][file] = content

    # Hash the commit
    commit_hash = hashlib.sha1(json.dumps(commit_data, sort_keys=True).encode()).hexdigest()
    commit_path = os.path.join(COMMITS_DIR, commit_hash)

    with open(commit_path, "w", encoding="utf-8") as f:
        json.dump(commit_data, f, indent=2)

    with open(HEAD_FILE, "w") as f:
        f.write(commit_hash)

    with open(INDEX_FILE, "w") as f:
        json.dump([], f)

    print(f"Committed as {commit_hash}")


def log():
    if not os.path.exists(HEAD_FILE):
        print("No commits yet.")
        return

    head = open(HEAD_FILE).read().strip()

    while head:
        commit_path = os.path.join(COMMITS_DIR, head)
        if not os.path.exists(commit_path):
            break

        with open(commit_path, "r") as f:
            data = json.load(f)

        print(f"Commit: {head}")
        print(f"Date:   {time.ctime(data['timestamp'])}")
        print(f"Message: {data['message']}\n")

        head = data.get("parent")


def diff(file_path):
    if not os.path.exists(file_path):
        print(f"{file_path} does not exist.")
        return

    with open(HEAD_FILE) as f:
        head = f.read().strip()

    if not head:
        print("No commits to diff against")
        return

    commit_path = os.path.join(COMMITS_DIR, head)
    if not os.path.exists(commit_path):
        print("Corrupted HEAD. Commit file not found.")
        return

    with open(commit_path) as f:
        data = json.load(f)

    committed_content = data["files"].get(file_path)
    if committed_content is None:
        print(f"{file_path} not found in last commit.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        working_content = f.read()

    diff_lines = difflib.unified_diff(
        committed_content.splitlines(),
        working_content.splitlines(),
        fromfile="committed",
        tofile="working",
        lineterm=""
    )

    print("\n".join(diff_lines) or "No changes.")

