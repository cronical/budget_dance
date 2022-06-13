#!/usr/bin/env python
'''Initialize the workbook'''
import argparse
from os import chdir,getcwd ,mkdir,walk
from os.path import exists, join,sep
from shutil import copy2,rmtree
import xml.etree.ElementTree as ET
import zipfile
from openpyxl import Workbook
from logs import get_logger

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
  file_paths = get_all_file_paths("./")
  # writing files to a zipfile
  with zipfile.ZipFile(dir+sep+zip_name,'w') as zip:
    for file in file_paths:
      zip.write(file)
  chdir(dir)
  
def create(filename):
  '''create the excel file, then insert the vba project'''
  logger=get_logger(__file__)
  logger.info(f'current working directory is {getcwd()}')
  assert not exists(filename),f'File name {filename} already exists'
  wb=Workbook()
  wb.save(filename)
  logger.info(f'initial file saved as {filename}')
  if exists('./tmp'):
    rmtree('./tmp')
  with zipfile.ZipFile(filename, 'r') as z:
    z.extractall('./tmp/')

  # In addition to the vba project (which is in an OLE2 format)
  # relationships and content types need to be correctly configured

  to_copy=['./tmp/xl/vbaProject.bin','./tmp/xl/_rels/workbook.xml.rels','./tmp/[Content_Types].xml']
  for dst in to_copy:
    src='./vba/'+dst.split(sep)[-1]
    copy2(src,dst)
    logger.info(f'copied {src} to {dst}')

  zip_up(filename,'tmp')
  logger.info(f're-wrote {filename}')
  #cleanup
  tmp='./tmp'
  rmtree(tmp)
  mkdir(tmp)
  logger.info(f'cleaned up {tmp}')
if __name__=='__main__':
    # execute only if run as a script
  parser = argparse.ArgumentParser(description ="initialize the forecast spreadsheet")
  parser.add_argument('out_file', help='provide the name of the output file')
  args=parser.parse_args()
  create(args.out_file)