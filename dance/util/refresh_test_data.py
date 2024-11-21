#! /usr/bin/env python
"""Recreate the test files by copying from production
"""
from shutil import ignore_patterns, copytree

test="/Users/george/argus/budget-dance/data"
prod="/Users/george/budget-dance/data"

ig_func=ignore_patterns("*.xlsx","config.yaml")

copytree(prod,test,ignore=ig_func,dirs_exist_ok=True)
msg="""
Ran copytree.
Use shell command diff to verify:
diff -qr data/ ~/budget-dance/data/
"""
print(msg)