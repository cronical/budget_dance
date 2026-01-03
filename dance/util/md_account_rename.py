#! /usr/bin/env python
"""Rename an account in the historical files in data/acct_bals/
"""
import argparse
from pathlib import Path
from dance.util.logs import get_logger

def main():
  logger=get_logger(__file__)
  parser = argparse.ArgumentParser(
    description='Renames a single account in the historical account balance files after similar rename in Moneydance.')
  parser.add_argument( 'old_name',help="Use quotes around account names with spaces.")
  parser.add_argument( 'new_name',help="Use quotes around account names with spaces.")
  args = parser.parse_args()
  data_path=Path("data")
  files=data_path.glob("**/*.tsv")
  for file in files:
    with open(file) as r:
      text=r.read()
    cnt=text.count(args.old_name)
    if cnt:
      text=text.replace(args.old_name,args.new_name)
      file.rename(file.parent/(file.stem+".bak"))
      with open(file,'w')as w:
        w.write(text)
      logger.info(f"Updated {cnt} occurrences in {file}")

  logger.info("Erasing backup files")
  for file in data_path.glob("**/*.bak"):
    file.unlink()

  logger.warning("Remember to review <config.yaml> for any needed changes")

if __name__=="__main__":
  main()