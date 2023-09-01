#!/usr/bin/env python
import argparse

from openpyxl import load_workbook
from openpyxl.workbook.defined_name import DefinedName

from dance.util.logs import get_logger
from dance.util.xl_formulas import prepare_formula
from dance.util.files import read_config

logger=get_logger(__file__)

def write_lambdas(target_file):
  config=read_config()
  wb=load_workbook(filename = target_file,keep_vba=True)
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
  parser = argparse.ArgumentParser(description ='write the lamda definitions to file')
  parser.add_argument('-workbook', default='data/test_wb.xlsm',help='provide the name of the existing workbook')
  args=parser.parse_args()
  write_lambdas(args.workbook)
  exit(0)