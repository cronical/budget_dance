#! /usr/bin/env python
'''Sets up logger, or if called from command line logs argument'''
import argparse
import logging
from os.path import sep

def get_logger(filename,level=logging.INFO):
  '''Get a logger given a name (like __file__).

  Uses the last part of the path less the extension as the name.
  Defaults to log level INFO.
  '''
  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)
  name=filename.split(sep)[-1]
  name=name.split('.')[0]
  return logging.getLogger(name)

if __name__=="__main__":
  logger=get_logger(__file__)
  description ='Writes args to log as a single line, use -d, -e, -w for debug, error, warning'
  parser = argparse.ArgumentParser(description=description)
  parser.add_argument('text', nargs='*')
  g=parser.add_mutually_exclusive_group()
  g.add_argument('--debug','-d',action='store_true')
  g.add_argument('--warning','-w',action='store_true')
  g.add_argument('--error','-e',action='store_true')
  args=parser.parse_args()
  msg=' '.join(args.text)
  t=args.debug+(2*args.warning)+(4*args.error)
  match t:
    case 0:
      logger.info(msg)
    case 1:
      logger.setLevel(logging.DEBUG)
      logger.debug(msg)
    case 2:
      logger.warning(msg)
    case 4:
      logger.error(msg)
  
