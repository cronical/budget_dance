#!/usr/bin/env python
# Set calculation options
import argparse

from openpyxl import load_workbook
from openpyxl.workbook.properties import CalcProperties

from dance.util.logs import get_logger
supported=['fullPrecision','fullCalcOnLoad']
logger=get_logger(__file__)

def calc_properties(target_file,calcId,option,value):
  # set workbook properties
  wb=load_workbook(filename = target_file,keep_vba=True)
  #   <calcPr calcId="191029" fullPrecision="0"/>
  val=[False,True][value]
  wb.calculation.calcId==calcId
  match option:
    case 'fullPrecision':
      wb.calculation.fullPrecision=val # False == Set precision as displayed
    case 'fullCalcOnLoad':
      wb.calculation.fullCalcOnLoad=val 

  wb.save(filename=target_file)
  logger.info('{} = {} written to workbook {}'.format(option,val,target_file))

if __name__=='__main__':
    # execute only if run as a script
  parser = argparse.ArgumentParser(description ='write the calculation option to file')
  parser.add_argument('option',choices=supported,help='Which of '+ ','.join(supported))
  parser.add_argument('value',type=int,choices=[0,1],help="0 for false, 1 for true")
  parser.add_argument('-workbook', default='data/test_wb.xlsm',help='provide the name of the existing workbook')
  parser.add_argument('-calcId',type=int,default=191029,help='value to set for calcID')
  args=parser.parse_args()
  calc_properties(args.workbook,args.calcId,args.option,args.value)
  exit(0)