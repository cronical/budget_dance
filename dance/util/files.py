'''DataFrame utilities'''
import warnings

import pandas as pd
import yaml

from dance.util.logs import get_logger

from os import chdir,getcwd ,walk
from os.path import join,sep
import zipfile
from dance.util.logs import get_logger

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


warnings.simplefilter(action='ignore', category=FutureWarning)

def tsv_to_df(filename,sep='\t',skiprows=0,nan_is_zero=True,string_fields=['Notes'],parse_shares=False):
  '''Grab the data from a Moneydance report and return a Pandas DataFrame.

  Typically the file has tab separated fields.

  Args:
    filename: The name of the file to read.
    sep: The field separator, default is tab.
    skiprows: the number of rows to skip at the start of the file.  Default is 0.
    nan_is_zero: whether to fill NaN values with zeros.  Default True.
    string_fields: a list of fields to consider as strings and not try to convert. Default is ['Notes']
    parse_shares: If True, move the word Shares from the amount column to a new column, Unit

  Returns: A data frame with numbers converted to floats and dates as datetime.

  Raises: FileNotFoundError

  '''
  logger=get_logger(__file__)
  try:
    df=pd.read_csv(filename,sep=sep,skiprows=skiprows,dtype='str') # keep as string because there are some clean ups needed
  except FileNotFoundError as e:
    logger.error('No file "{}"'.format(filename))
    raise f'file not found {filename}' from e 
  cols=df.columns
  for col in cols[1:]:
    if col != 'Date' and col not in string_fields:
      if nan_is_zero:
        df.loc[:,col]=df[col].fillna(value='0.00')
      df.loc[:,col]=df[col].str.replace('--','0.00') # occurs in performance report
      df.loc[:,col]=df[col].str.replace('None','0.00') # occurs in performance report
      # remove punctuation and conver parens to negative
      df.loc[:,col]=df[col].str.replace(r'[\$,)]','',regex=True)
      df.loc[:,col]=df[col].str.replace('[(]','-',regex=True)
      if parse_shares:
        if col=='Amount':
          df[[col,'Unit']] = df[col].str.strip(' ').str.split(' ',expand=True)
      df.loc[:,col]=df[col].astype(float)
    if col == 'Date':
      df[col] = pd.to_datetime(df[col])

  return df

def read_config():
  '''Reads the config
  
  returns: the config as a dict
  
  raises FileNotFoundError
  '''
  logger=get_logger(__file__)
  fn='data/setup.yaml'
  try:
    with open(fn) as y:
      config=yaml.load(y,yaml.Loader)
  except FileNotFoundError as e:
    raise f'file not found {fn}' from e
  logger.debug('read {} as config'.format(fn))
  return config
