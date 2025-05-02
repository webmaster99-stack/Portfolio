import os
import json
import time
import tempfile
import shutil
import pytest
from io import StringIO
from unittest.mock import patch, mock_open
from myvcs import commands


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(temp_dir)

    # Create some test files
    with open("test_file.txt", "w") as f:
        f.write("test content")
    with open("another_file.txt", "w") as f:
        f.write("more content")

    yield temp_dir

    # Cleanup
    os.chdir(original_dir)
    shutil.rmtree(temp_dir)


def test_init(temp_dir):
    """Test initialization of VCS repository"""
    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.init()

        assert os.path.exists(commands.VCS_DIR)
        assert os.path.exists(commands.COMMITS_DIR)
        assert os.path.exists(commands.INDEX_FILE)
        assert os.path.exists(commands.HEAD_FILE)

        with open(commands.INDEX_FILE, 'r') as f:
            assert json.load(f) == []

        with open(commands.HEAD_FILE, 'r') as f:
            assert f.read() == ""

        assert "Initialized empty VCS repository" in fake_out.getvalue()


def test_add_valid_file(temp_dir):
    """Test adding a valid file to staging area"""
    commands.init()

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.add("test_file.txt")

        with open(commands.INDEX_FILE, 'r') as f:
            staged = json.load(f)
            assert "test_file.txt" in staged

        assert "Added test_file.txt to the staging area" in fake_out.getvalue()


def test_add_nonexistent_file(temp_dir):
    """Test adding a nonexistent file to staging area"""
    commands.init()

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.add("nonexistent_file.txt")

        with open(commands.INDEX_FILE, 'r') as f:
            staged = json.load(f)
            assert "nonexistent_file.txt" not in staged

        assert "nonexistent_file.txt does not exist" in fake_out.getvalue()


def test_add_already_staged_file(temp_dir):
    """Test adding an already staged file"""
    commands.init()
    commands.add("test_file.txt")

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.add("test_file.txt")

        with open(commands.INDEX_FILE, 'r') as f:
            staged = json.load(f)
            assert "test_file.txt" in staged
            assert staged.count("test_file.txt") == 1  # Should not be duplicated

        assert "test_file.txt is already staged" in fake_out.getvalue()


def test_remove_staged_file(temp_dir):
    """Test removing a staged file"""
    commands.init()
    commands.add("test_file.txt")

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.remove("test_file.txt")

        with open(commands.INDEX_FILE, 'r') as f:
            staged = json.load(f)
            assert "test_file.txt" not in staged

        assert "Removed test_file.txt from the staging area" in fake_out.getvalue()


def test_remove_unstaged_file(temp_dir):
    """Test removing a file that was not staged"""
    commands.init()

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.remove("test_file.txt")

        with open(commands.INDEX_FILE, 'r') as f:
            staged = json.load(f)
            assert "test_file.txt" not in staged

        assert "test_file.txt was not staged" in fake_out.getvalue()


def test_commit_with_files(temp_dir):
    """Test committing staged files"""
    commands.init()
    commands.add("test_file.txt")

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.commit("Initial commit")

        # Check that the staging area is cleared
        with open(commands.INDEX_FILE, 'r') as f:
            assert json.load(f) == []

        # Check that HEAD is updated
        with open(commands.HEAD_FILE, 'r') as f:
            head = f.read().strip()
            assert head != ""

        # Check that the commit file exists
        commit_path = os.path.join(commands.COMMITS_DIR, head)
        assert os.path.exists(commit_path)

        # Check the commit content
        with open(commit_path, 'r') as f:
            commit_data = json.load(f)
            assert commit_data["message"] == "Initial commit"
            assert "test_file.txt" in commit_data["files"]
            assert commit_data["files"]["test_file.txt"] == "test content"
            assert commit_data["parent"] is None

        assert "Committed as" in fake_out.getvalue()


def test_commit_no_files(temp_dir):
    """Test committing with no staged files"""
    commands.init()

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.commit("Empty commit")

        assert "No files to commit" in fake_out.getvalue()


def test_commit_chain(temp_dir):
    """Test chain of commits with parent references"""
    commands.init()

    # First commit
    commands.add("test_file.txt")
    commands.commit("First commit")

    with open(commands.HEAD_FILE, 'r') as f:
        first_commit = f.read().strip()

    # Change file and make second commit
    with open("test_file.txt", "w") as f:
        f.write("modified content")

    commands.add("test_file.txt")
    commands.commit("Second commit")

    with open(commands.HEAD_FILE, 'r') as f:
        second_commit = f.read().strip()

    # Check parent reference
    commit_path = os.path.join(commands.COMMITS_DIR, second_commit)
    with open(commit_path, 'r') as f:
        commit_data = json.load(f)
        assert commit_data["parent"] == first_commit


def test_log_with_commits(temp_dir):
    """Test log output with existing commits"""
    commands.init()
    commands.add("test_file.txt")
    commands.commit("First commit")

    # Add another commit
    with open("test_file.txt", "w") as f:
        f.write("modified content")
    commands.add("test_file.txt")
    commands.commit("Second commit")

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.log()

        output = fake_out.getvalue()
        assert "Commit:" in output
        assert "First commit" in output
        assert "Second commit" in output
        assert output.count("Commit:") == 2


def test_log_no_commits(temp_dir):
    """Test log output with no commits"""
    commands.init()

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.log()

        assert "No commits yet" in fake_out.getvalue()


def test_diff_with_changes(temp_dir):
    """Test diff output when file has been changed since last commit"""
    commands.init()
    commands.add("test_file.txt")
    commands.commit("Initial commit")

    # Modify the file
    with open("test_file.txt", "w") as f:
        f.write("modified content")

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.diff("test_file.txt")

        output = fake_out.getvalue()
        assert "--- committed" in output
        assert "+++ working" in output
        assert "-test content" in output
        assert "+modified content" in output


def test_diff_without_changes(temp_dir):
    """Test diff output when file has not changed since last commit"""
    commands.init()
    commands.add("test_file.txt")
    commands.commit("Initial commit")

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.diff("test_file.txt")

        assert "No changes" in fake_out.getvalue()


def test_diff_nonexistent_file(temp_dir):
    """Test diff with a file that doesn't exist"""
    commands.init()
    commands.add("test_file.txt")
    commands.commit("Initial commit")

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.diff("nonexistent_file.txt")

        assert "nonexistent_file.txt does not exist" in fake_out.getvalue()


def test_diff_uncommitted_file(temp_dir):
    """Test diff with a file that hasn't been committed"""
    commands.init()
    commands.add("test_file.txt")
    commands.commit("Initial commit")

    with open("new_file.txt", "w") as f:
        f.write("new content")

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.diff("new_file.txt")

        assert "new_file.txt not found in last commit" in fake_out.getvalue()


def test_diff_no_commits(temp_dir):
    """Test diff when there are no commits"""
    commands.init()

    with patch('sys.stdout', new=StringIO()) as fake_out:
        commands.diff("test_file.txt")

        assert "No commits to diff against" in fake_out.getvalue()