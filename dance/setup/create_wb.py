#!/usr/bin/env python
'''Initialize the workbook'''
import argparse
from os import chdir,getcwd ,mkdir,walk
from os.path import exists, join,sep
from shutil import copy2,rmtree
from sys import exit
import zipfile
from openpyxl import load_workbook
from dance.util.logs import get_logger
from dance.setup.setup_tabs import refresh_sheets

def get_all_file_paths(directory):
  '''zip does one file at a time so get the list'''
  # initializing empty file paths list
  file_paths = []

  # crawling through directory and subdirectories
  for root, _, files in walk(directory):
    for filename in files:
      # join the two strings in order to form the full filepath.
      filepath = join(root, filename)
      file_paths.append(filepath)

  # returning all file paths
  return file_paths

def zip_up(zip_name,directory):
  '''put a directory into a zipfile'''
  dir=getcwd()
  chdir(directory)
  file_paths = get_all_file_paths('./')
  # writing files to a zipfile
  with zipfile.ZipFile(dir+sep+zip_name,'w') as zip:
    for file in file_paths:
      zip.write(file)
  chdir(dir)

def create(filename,overwrite=False):
  '''Create the excel file, insert the vba project and then add in the worksheets.
  The vba project requires some special handling.  It has references to the worksheets.
  The vba code has previously been extracted and is inserted by unzipping the xslm file and replacing certain parts before rezipping it.
  It appears that this will get confused under circumstances where the worksheet list from the overlay does not match that in the stored vba project.
  This will result a ThisWorkbook1 in addition to the expected ThisWorkbook item undert "Microsoft Excel Objects", causing code crashes.
  The solution at this point is to use an empty macro enabled worksheet to start with.  This has a sheet named accounts.
  Excel itself does not allow this to be done, but the code here does that, before it recreates that sheet.
  This manouever appears to leave the VBA project consistent with the other components of the spreadsheet.
  '''
  logger=get_logger(__file__)
  logger.info('current working directory is {}'.format(getcwd()))
  if not overwrite:
    logger.error('File name {} already exists, use -o to force overwrite'.format(filename))
    exit(-1)
  wb=load_workbook('data/empty_template.xlsm',keep_vba=True)
  wb.save(filename)
  logger.info('initial file saved as {}'.format(filename))



  logger.info('starting copy of vba')
  if exists('./tmp'):
    rmtree('./tmp')
  with zipfile.ZipFile(filename, 'r') as z:
    z.extractall('./tmp/')

  # In addition to the vba project (which is in an OLE2 format)
  # relationships and content types need to be correctly configured
  # shared strings seems to be required by openpyxl if the others are provided
  to_copy=['./tmp/xl/vbaProject.bin','./tmp/xl/_rels/workbook.xml.rels','./tmp/[Content_Types].xml',
  './tmp/xl/sharedStrings.xml']
  for dst in to_copy:
    src='./vba/'+dst.split(sep)[-1]
    copy2(src,dst)
    logger.info('copied {} to {}'.format(src,dst))

  zip_up(filename,'tmp')
  logger.info('re-wrote {}'.format(filename))
  #cleanup
  tmp='./tmp'
  rmtree(tmp)
  mkdir(tmp)
  logger.info('cleaned up {}'.format(tmp))

  refresh_sheets(filename,overwrite)


if __name__=='__main__':
    # execute only if run as a script
  parser = argparse.ArgumentParser(description ='initialize the forecast spreadsheet')
  parser.add_argument('out_file', help='provide the name of the output file')
  parser.add_argument('-o','--overwrite',default=False, action='store_true',help='force overwrite if file already exists')
  args=parser.parse_args()
  create(args.out_file,args.overwrite)
  