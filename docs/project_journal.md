# DiffInsight Project Journal

## 10 June 2026

### Milestone 1 - Commit Mining

Objective:
Build a pipeline to extract commit history from a Git repository.

Activities:
- Cloned scikit-learn repository
- Installed GitPython
- Created extract_commits.py
- Extracted 5000 commits
- Stored results in dataset_raw.csv

Columns collected:
- commit_hash
- date
- message
- diff
- python_files_changed
- files_changed
- insertions
- deletions

Issues encountered:
- Repo path error (NoSuchPathError)
- Fixed by moving repository into repos folder

Improvement
- Fixed file path handling using absolute/structured project directories
- Verified dataset writing to data/raw folder
- Ran pipeline successfully on 100 commits and then scaled to 5000 commits

Results:
- Dataset generated successfully
- Only 14 commits had missing diffs
- Missing diffs corresponded mainly to merge, documentation and empty commits

Status:
Completed