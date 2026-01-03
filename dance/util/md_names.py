#! /usr/bin/env python
"""Renames and/or moves the .txt files which are Moneydance reports saved as tsv
"""
import argparse
from pathlib import Path
from dance.util.prompts import prompt_no_yes
from dance.util.logs import get_logger

def main():
  logger=get_logger(__file__)
  parser = argparse.ArgumentParser(
    description='Prepares reports saved from Moneydance by fixing extension and relocating as needed')
  parser.add_argument( 'year', type=int,
                      help='provide the year for the account balances and investment performance')
  args = parser.parse_args()
  data_path=Path("data")
  files=data_path.glob("*.txt")
  to_folder=("acct_bals","invest_p")
  for file in files:
    stem=remove_prefix(file.stem)
    if stem in to_folder:
      folder=data_path / stem
      existing=folder.glob('*.tsv')
      existing=[int(a.stem) for a in existing]
      if args.year in existing: # safety check to allow only replacing most recent
        if args.year != max(existing):
          print(f"Do you really want to replace {args.year}.tsv in {folder.name}.")
          prompt_no_yes()
      new= folder / f'{args.year}.tsv'
      file.replace(new)
    else:
      stem = remove_prefix(file.stem)
      new = data_path / f'{stem}.tsv'
      file.replace(new)
    logger.info(new)

def remove_prefix(file_stem):
  stem = "_".join(file_stem.split("_")[1:])
  return stem


if __name__=="__main__":
  main()