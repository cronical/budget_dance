#!/usr/bin/env python
'''Initialize the workbook'''
import argparse
from os import getcwd #,mkdir
from os.path import exists, sep
#from shutil import copy2,rmtree
from sys import exit
#import zipfile

from openpyxl import Workbook # load_workbook

from pyinstrument import Profiler

#from dance.util.files import zip_up
from dance.util.logs import get_logger
from dance.setup.lambdas import write_lambdas
from dance.setup.setup_tabs import refresh_sheets



def create(filename,overwrite=False):
  '''Create the excel file, then add in the worksheets.
  Previously: insert the vba project 
  The vba project requires some special handling.  It has references to the worksheets.
  The vba code has previously been extracted and is inserted by unzipping the xslm file and replacing certain parts before rezipping it.
  It appears that this will get confused under circumstances where the worksheet list from the overlay does not match that in the stored vba project.
  This will result a ThisWorkbook1 in addition to the expected ThisWorkbook item undert "Microsoft Excel Objects", causing code crashes.
  The solution at this point is to use an empty macro enabled worksheet to start with.  This has a sheet named accounts.
  Excel itself does not allow this to be done, but the code here does that, before it recreates that sheet.
  This manouever appears to leave the VBA project consistent with the other components of the spreadsheet.
  '''
  logger=get_logger(__file__)
  logger.debug('current working directory is {}'.format(getcwd()))
  if exists(filename):
    if not overwrite:
      logger.error('File name {} already exists, use -o to force overwrite'.format(filename))
      exit(-1)
  #wb=load_workbook('data/empty_template.xlsm')
  wb=Workbook()
  wb.save(filename)
  logger.debug('initial file saved as {}'.format(filename))



  #logger.debug('starting copy of vba')
  #if exists('./tmp'):
  #  rmtree('./tmp')
  #with zipfile.ZipFile(filename, 'r') as z:
  #  z.extractall('./tmp/')

  # In addition to the vba project (which is in an OLE2 format)
  # relationships and content types need to be correctly configured
  # shared strings seems to be required by openpyxl if the others are provided
  #to_copy=['./tmp/xl/vbaProject.bin','./tmp/xl/_rels/workbook.xml.rels','./tmp/[Content_Types].xml',
  #'./tmp/xl/sharedStrings.xml']
  #for dst in to_copy:
  #  src='./vba/'+dst.split(sep)[-1]
  #  copy2(src,dst)
  #  logger.debug('copied {} to {}'.format(src,dst))

  #zip_up(filename,'tmp')
  #logger.info('Initialized {} with vba'.format(filename))
  #cleanup
  #tmp='./tmp'
  #rmtree(tmp)
  #mkdir(tmp)
  #logger.debug('cleaned up {}'.format(tmp))

  write_lambdas(filename)
  refresh_sheets(filename,overwrite)



if __name__=='__main__':
    # execute only if run as a script
  parser = argparse.ArgumentParser(description ='initialize the forecast spreadsheet')
  parser.add_argument('out_file', help='provide the name of the output file')
  parser.add_argument('-o','--overwrite',default=False, action='store_true',help='force overwrite if file already exists')
  args=parser.parse_args()
  profiler = Profiler()
  profiler.start()

  # code you want to profile
  create(args.out_file,args.overwrite)

  profiler.stop()

  profiler.print()
  exit(0)
  