#! /usr/bin/env python
'''Open up excel for file inspection'''
from os.path import exists
from shutil import rmtree
import zipfile
from dance.util.files import read_config
from dance.util.logs import get_logger

def extract(filename):
  if exists('./tmp'):
    rmtree('./tmp')
  with zipfile.ZipFile(filename, 'r') as z:
    z.extractall('./tmp/')

if __name__=="__main__":
  logger=get_logger(__file__)
  filename=read_config()['workbook']
  extract(filename)
  logger.info("%s unzipped in ./tmp"%filename)
