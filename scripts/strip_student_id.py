"""
strip_student_id.py
===================
Removes the student ID "k21194535" from all 5 HTML files and
replaces the page <title> with a professional title.

Run this ONCE from the repo root before your first git commit:
    python scripts/strip_student_id.py

What it changes in each HTML file:
  BEFORE: <h3 class="pt-4 pb-4 px-1">Ashish Menghani-k21194535</h3>
  AFTER:  <h3 class="pt-4 pb-4 px-1">Ashish Menghani</h3>

  BEFORE: <title>Data Visualization</title>
  AFTER:  <title>DJIA Financial Visualisation | D3.js Dashboard</title>

Safe to run multiple times — won't double-apply changes.
"""

import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HTML_FILES = [
    "index.html",
    os.path.join("html", "CandleStick.html"),
    os.path.join("html", "LineChart.html"),
    os.path.join("html", "ComparisionChart.html"),
    os.path.join("html", "LineChart2.html"),
]

REPLACEMENTS = [
    # Remove student ID from navbar heading
    (
        r'<h3 class="pt-4 pb-4 px-1">Ashish Menghani-k21194535</h3>',
        '<h3 class="pt-4 pb-4 px-1">Ashish Menghani</h3>',
    ),
    # Replace generic page title
    (
        "<title>Data Visualization</title>",
        "<title>DJIA Financial Visualisation | D3.js Dashboard</title>",
    ),
    # Safety catch — any remaining student ID pattern
    (
        r"k21194535",
        "",
    ),
    (
        r"K21194535",
        "",
    ),
]


def strip_file(filepath: str):
    full_path = os.path.join(REPO_ROOT, filepath)

    if not os.path.exists(full_path):
        print(f"  SKIP (not found): {filepath}")
        return

    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content)

    if content != original:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  CLEANED: {filepath}")
    else:
        print(f"  ALREADY CLEAN: {filepath}")


def verify_clean(filepath: str):
    full_path = os.path.join(REPO_ROOT, filepath)
    if not os.path.exists(full_path):
        return
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
    for id_string in ["k21194535", "K21194535", "21194535"]:
        if id_string in content:
            print(f"  ⚠️  WARNING: '{id_string}' still found in {filepath}")
            return
    print(f"  ✓ VERIFIED CLEAN: {filepath}")


print("\n=== Strip Student ID from HTML Files ===\n")
print("Step 1: Applying replacements...")
for f in HTML_FILES:
    strip_file(f)

print("\nStep 2: Verifying no student IDs remain...")
for f in HTML_FILES:
    verify_clean(f)

print("\nDone. Safe to git add and commit.\n")
