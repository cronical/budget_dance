#! /usr/bin/env python
'''reseal file opened by reveal'''
from shutil import rmtree
from dance.util.files import read_config
from dance.util.files import zip_up
from dance.util.logs import get_logger

logger=get_logger(__file__)

def zip(filename):
  zip_up(filename,'tmp')
  rmtree('./tmp')
  logger.debug("removed ./tmp")
  
if __name__=="__main__":
  filename=read_config()['workbook']
  zip(filename)
  logger.info("%s re-zipped"%filename)
