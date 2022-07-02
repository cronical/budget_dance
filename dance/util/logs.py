'''Sets up logger'''

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
