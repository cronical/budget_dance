#!/usr/bin/env python
import argparse

from openpyxl import load_workbook
from openpyxl.workbook.defined_name import DefinedName

from dance.util.logs import get_logger
from dance.util.xl_formulas import prepare_formula
from dance.util.files import read_config

config=read_config()
logger=get_logger(__file__)

def write_lambdas(target_file):
  wb=load_workbook(filename = target_file)#)
  cnt=0
  for lam in config['lambdas']:
    f=prepare_formula(lam['formula'])
    assert f.startswith("="),"lambda formula does not start with = " + f
    f=f[1:]
    d=DefinedName(lam["name"],comment=lam["comment"],attr_text=f)
    wb.defined_names.add(d)   
    cnt=cnt+1 

  wb.save(filename=target_file)
  logger.info('{} Lambda functions written to workbook {} saved'.format(cnt,target_file))

if __name__=='__main__':
    # execute only if run as a script
  default_wb=config['workbook']
  parser = argparse.ArgumentParser(description ='write the lamda definitions to file')
  parser.add_argument('-workbook', default=default_wb,help=f'Target workbook. Default: {default_wb}')
  args=parser.parse_args()
  write_lambdas(args.workbook)
  exit(0)