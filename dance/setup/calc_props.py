#!/usr/bin/env python
# Set calculation options
import argparse

from openpyxl import load_workbook
from openpyxl.workbook.properties import CalcProperties

from dance.util.logs import get_logger

logger=get_logger(__file__)

def calc_properties(target_file):
  # set workbook properties
  wb=load_workbook(filename = target_file,keep_vba=True)
  cnt=0
  #   <calcPr calcId="191029" fullPrecision="0"/>
  assert wb.calculation.calcId==191029, 'calcId: expected 191029, is %d'%wb.calculation.calcId
  wb.calculation.fullPrecision=False # Set precision as displayed
  cnt=cnt+1 

  wb.save(filename=target_file)
  logger.info('{} calculation options written to workbook {}'.format(cnt,target_file))

if __name__=='__main__':
    # execute only if run as a script
  parser = argparse.ArgumentParser(description ='write the calculation options to file')
  parser.add_argument('-workbook', default='data/test_wb.xlsm',help='provide the name of the existing workbook')
  args=parser.parse_args()
  calc_properties(args.workbook)
  exit(0)