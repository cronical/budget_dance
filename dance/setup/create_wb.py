#!/usr/bin/env python
'''Initialize the workbook'''
import argparse
from os import getcwd #,mkdir
from os.path import exists
from sys import exit

from openpyxl import Workbook # load_workbook

from dance.util.logs import get_logger
from dance.setup.lambdas import write_lambdas
from dance.setup.setup_tabs import refresh_sheets

def create(filename,overwrite=False):
  '''Create the excel file, then add in the worksheets.
  '''
  logger=get_logger(__file__)
  logger.debug('current working directory is {}'.format(getcwd()))
  if exists(filename):
    if not overwrite:
      logger.error('File name {} already exists, use -o to force overwrite'.format(filename))
      exit(-1)
  wb=Workbook()
  wb.save(filename)
  logger.debug('initial file saved as {}'.format(filename))
  write_lambdas(filename)
  refresh_sheets(filename,overwrite)

if __name__=='__main__':
    # execute only if run as a script
  parser = argparse.ArgumentParser(description ='initialize the forecast spreadsheet')
  parser.add_argument('out_file', help='provide the name of the output file')
  parser.add_argument('-o','--overwrite',default=False, action='store_true',help='force overwrite if file already exists')
  parser.add_argument('-p','--profile',default=False,action='store_true',help='Use performance profiler')
  args=parser.parse_args()
  if args.profile:
    from pyinstrument import Profiler
    profiler = Profiler()
    profiler.start()

  # code to profile
  create(args.out_file,args.overwrite)

  if args.profile:
    profiler.stop()
    profiler.print()
    
  exit(0)
  