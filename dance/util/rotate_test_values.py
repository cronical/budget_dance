#! /usr/bin/env python
"""Use this to drop the first know test value and add a zero at the end
"""
import argparse
import json
from pathlib import Path
from dance.util.logs import get_logger

def main():
  logger=get_logger(__file__)
  parser = argparse.ArgumentParser(description='Use this to drop the first know test value and add a zero at the end')
  parser.add_argument('year', type=int, help="Provide year to remove it from the ignore lists")
  args = parser.parse_args()
  data_path=Path("data")
  file=data_path /"known_test_values.json"
  with open(file) as r:
    test_cases = json.load(r)
  cnt=0
  for table,cases in test_cases.items():
    for row,value in cases.items():
      if row.startswith('ignore'):
        y=f"Y{args.year}"
        if y in value:
          value.pop(value.index(y))
      else:
        value=value[1:]+[0]
        cnt+=1
      cases[row]=value
    test_cases[table]=cases
  file.rename(file.parent/(file.stem+".bak"))
  with open(file,'w')as w:
    json.dump(test_cases,w)
  logger.info(f"Updated {cnt} items in {file}")

  logger.info("Erasing backup files")
  for file in data_path.glob("**/*.bak"):
    file.unlink()


if __name__=="__main__":
  main()