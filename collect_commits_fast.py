# src/data_collection/collect_commits_fast.py

import requests
import pandas as pd
import re
import os
import time
from datetime import datetime
from config import TOKEN

REPO = "scikit-learn/scikit-learn"
HEADERS = {"Authorization": f"token {TOKEN}"}
TODAY = datetime.now().strftime("%Y-%m-%d")

DATA_DIR = "data/raw"
os.makedirs(DATA_DIR, exist_ok=True)

# Bug-fix keywords
BUG_KEYWORDS = re.compile(
    r'\b(fix|bug|defect|error|issue|fault|patch|hotfix|closes|resolves)\b',
    re.IGNORECASE
)

def is_bug_fix_commit(message):
    return bool(BUG_KEYWORDS.search(message))

def safe_request(url, params=None, retries=3):
    for _ in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=10)
            if r.status_code == 200:
                return r
            time.sleep(2)
        except requests.exceptions.RequestException:
            time.sleep(2)
    return None

def extract_changed_functions(patch):
    if not patch:
        return []
    pattern = re.compile(r'@@.*@@\s+def\s+(\w+)')
    return pattern.findall(patch)

print(f"🚀 Collecting commits for {TODAY}...")

# Step 1: Get commits
response = safe_request(
    f"https://api.github.com/repos/{REPO}/commits",
    params={"per_page": 100}
)

if not response:
    print("❌ Failed to fetch commits")
    exit()

commits = response.json()
print(f"Found {len(commits)} commits")

file_data = []

# Step 2: Process commits
for i, commit in enumerate(commits):
    sha = commit["sha"]
    message = commit["commit"]["message"]
    date = commit["commit"]["author"]["date"]
    author = commit["commit"]["author"]["name"]
    is_fix = is_bug_fix_commit(message)

    detail = safe_request(
        f"https://api.github.com/repos/{REPO}/commits/{sha}"
    )

    if not detail:
        continue

    detail_json = detail.json()

    if "files" not in detail_json:
        continue

    for file in detail_json["files"]:
        if not file["filename"].endswith(".py"):
            continue

        patch = file.get("patch", "")
        additions = file["additions"]
        deletions = file["deletions"]

        file_data.append({
            "commit_sha": sha,
            "date": date,
            "author": author,
            "filename": file["filename"],
            "commit_message": message[:200],
            "is_bug_fix": is_fix,
            "patch": patch,
            "changed_functions": ", ".join(extract_changed_functions(patch)),
            "additions": additions,
            "deletions": deletions,
            "changes": additions + deletions,
            "defect_label": 1 if is_fix else 0,
        })

    # Rate control
    if (i + 1) % 10 == 0:
        print(f"Processed {i+1}/{len(commits)}")
        time.sleep(1)

# Step 3: Save
df = pd.DataFrame(file_data)
output_file = f"{DATA_DIR}/diffs_{TODAY}.csv"
df.to_csv(output_file, index=False)

print(f"✅ Saved {len(file_data)} records to {output_file}")