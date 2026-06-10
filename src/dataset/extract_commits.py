# extract_commits.py

from git import Repo
import csv

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPO_PATH = PROJECT_ROOT / "repos" / "scikit-learn"
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "dataset_raw.csv"

MAX_COMMITS = 5000            # Set to None for all commits
MAX_DIFF_LENGTH = 10000        # Prevent huge CSV files

# --------------------------------------------------
# LOAD REPOSITORY
# --------------------------------------------------

repo = Repo(REPO_PATH)

# --------------------------------------------------
# WRITE DATASET
# --------------------------------------------------

with open(
    OUTPUT_FILE,
    mode="w",
    newline="",
    encoding="utf-8"
) as csvfile:

    writer = csv.DictWriter(
        csvfile,
        fieldnames=[
            "commit_hash",
            "date",
            "message",
            "diff",
            "python_files_changed",
            "files_changed",
            "insertions",
            "deletions"
        ]
    )

    writer.writeheader()

    for i, commit in enumerate(repo.iter_commits()):

        # Stop after N commits (for testing)
        if MAX_COMMITS and i >= MAX_COMMITS:
            break

        # Skip initial commit
        if len(commit.parents) == 0:
            continue

        parent = commit.parents[0]

        # ------------------------------------------
        # Extract diff text
        # ------------------------------------------

        diff_text = ""

        try:
            diffs = parent.diff(commit, create_patch=True)

            for diff in diffs:

                if diff.diff:

                    patch = diff.diff.decode(
                        "utf-8",
                        errors="ignore"
                    )

                    diff_text += patch

        except Exception as e:
            print(f"Error reading diff for {commit.hexsha}: {e}")
            continue

        # Limit diff size
        diff_text = diff_text[:MAX_DIFF_LENGTH]

        # ------------------------------------------
        # Check if Python files changed
        # ------------------------------------------

        try:
            python_files_changed = any(
                d.b_path
                and d.b_path.endswith(".py")
                for d in parent.diff(commit)
            )
        except:
            python_files_changed = False

        # ------------------------------------------
        # Commit statistics
        # ------------------------------------------

        stats = commit.stats.total

        row = {
            "commit_hash": commit.hexsha,
            "date": commit.committed_datetime,
            "message": commit.message.strip(),
            "diff": diff_text,
            "python_files_changed": python_files_changed,
            "files_changed": stats.get("files", 0),
            "insertions": stats.get("insertions", 0),
            "deletions": stats.get("deletions", 0)
        }

        writer.writerow(row)

        # Progress update
        if i % 100 == 0:
            print(f"Processed {i} commits...")

print("\nDataset extraction complete!")
print(f"Saved to: {OUTPUT_FILE}")