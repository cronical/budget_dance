#!/usr/bin/env python
'''Initialize the workbook'''
import argparse
from os import getcwd #,mkdir
from os.path import exists, split, join
from sys import exit

from openpyxl import Workbook # load_workbook

from dance.util.logs import get_logger
from dance.book.lambdas import write_lambdas
from dance.book.add_sheets import refresh_sheets

def create(filename,overwrite=False):
  '''Create the excel file, then add in the worksheets.
  Raises error if file is open by Excel
  '''
  logger=get_logger(__file__)
  logger.info('current working directory is {}'.format(getcwd()))
  if exists(filename):
    if not overwrite:
      logger.error('File name {} already exists, use -o to force overwrite'.format(filename))
      exit(-1)
  # check for open file
  path,file=split(filename)
  temp_file=join(path,"~$"+file)
  if exists(temp_file):
    raise ValueError(f"{temp_file} exists indicating target is open.")
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
  