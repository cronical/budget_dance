#! /usr/bin/env python
""" Copy the theme defined in config into the excel file
"""
import os
from shutil import copy
import sys
from pathlib import Path
from dance.util.files import read_config
from dance.util.logs import get_logger
from dance.util import reveal, reseal

def set_theme():
  """ Perform the set """
  logger=get_logger(__file__)
  config=read_config()
  theme=config['theme']+".xml"
  src=locate() / theme

  filename=config['workbook']
  reveal.extract(filename)
  copy(src, "tmp/xl/theme/theme1.xml")
  reseal.zip(filename)

  logger.info("Excel theme set to %s"%theme)

def locate():
  """determines location of theme folder based on deployment
  """
  dev='dance/themes'
  if os.path.exists(dev): # its the development deployment
    return Path(dev)
  
  # expect to locate in the site packages
  base =   Path(os.environ['VIRTUAL_ENV']) 
  ver='python'+'.'.join(sys.version.split(' ')[0].split('.')[0:2])
  path=base.joinpath('lib',ver,'site-packages',dev)
  return path

if __name__=='__main__':
  set_theme()