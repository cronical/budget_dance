#! /usr/bin/env python
'''Open up excel for file inspection'''
from os.path import exists
from shutil import rmtree
import zipfile
from dance.util.files import read_config
from dance.util.logs import get_logger

logger=get_logger(__file__)
filename=read_config()['workbook']

if exists('./tmp'):
  rmtree('./tmp')
with zipfile.ZipFile(filename, 'r') as z:
  z.extractall('./tmp/')
logger.info("%s unzipped in ./tmp"%filename)
