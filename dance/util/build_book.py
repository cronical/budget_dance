#! /usr/bin/env python
""" Driver to build the workbook
(replaces shell script)
"""
from os.path import exists
import subprocess
import sys
from time import sleep

from dance.preserve_changed import load_sparse
from dance.ytd import load_and_forward

from dance.book.calc_props import calc_properties
from dance.book.create import create

from dance.util.files import read_config
from dance.util.doc_lambda import gen_lambda_docs
from dance.util.logs import get_logger
from dance.util.theme import set_theme

from dance.util.cross_check import verify


def main():
  config=read_config()
  logger=get_logger(__name__)
  try:
    create(config['workbook'],overwrite=True)
  except ValueError as e:
    logger.error(e)
    sys.exit(-1)

  # document the lambdas
  if exists("docs/"): # only generate lamda docs in dev (this needs more thought)
    gen_lambda_docs()

  # load preserved values
  load_sparse(config,config['workbook'],'./data/preserve.json')

  # pull in the ytd reprojections
  load_and_forward(config,'./data/ytd_data.json')

  # Setting the workbook theme as one of the items in the themes folder
  set_theme()

  # Calc properties
  calc_properties(config['workbook'],191029,"fullPrecision",0)  # 0 means Set precision as displayed
  calc_properties(config['workbook'],191029,"fullCalcOnLoad",1) # yes recalc on open

  # open, calculate and save
  # this allows Excel to compute the formulas and establish some hidden defined names

  logger.info("opening the file to compute formulas")
  output=subprocess.run(["open",config['workbook']])
  if output.returncode!=0:
    logger.error(f"Command to launch excel failed with return code {output.returncode}")
  else:    
    sleep(2)# avoid:  execution error: Microsoft Excel got an error: Parameter error. (-50)

    for cmd in ('''tell app "Microsoft Excel" to save''','''tell app "Microsoft Excel" to quit'''):
      output=subprocess.run(["osascript","-e",cmd])
      if output.returncode!=0:
        logger.error(f"Command ( {cmd} ) to excel failed with return code {output.returncode}")
    logger.info("Calculations done and file saved.")      

  score=verify(config['workbook'],'*')
  if score==0:
    score=100
  logger.info(f"Score is {score} pct")

if __name__=="__main__":
  main()
