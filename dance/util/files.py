'''DataFrame utilities'''
import yaml
import pandas as pd


from dance.util.logs import get_logger

def tsv_to_df(filename,sep='\t',skiprows=0,nan_is_zero=True):
  '''Grab the data from a Moneydance report and return a Pandas DataFrame.

  Typically the file has tab separated fields.

  Args:
    filename: The name of the file to read.
    sep: The field separator, default is tab.
    skiprows: the number of rows to skip at the start of the file.  Default is 0.
    nan_is_zero: whether to fill NaN values with zeros.  Default True.

  Returns: A data frame with numbers converted to floats and dates as datetime.

  Raises: FileNotFoundError

  '''
  logger=get_logger(__file__)
  try:
    df=pd.read_csv(filename,sep=sep,skiprows=skiprows,dtype='str') # keep as string because there are some clean ups needed
  except FileNotFoundError:
    logger.error('No file "{}"'.format(filename))
    raise
  cols=df.columns
  for col in cols[1:]:
    if col != 'Date' and col != 'Notes':
      if nan_is_zero:
        df.loc[:,col]=df[col].fillna(value='0.00')
      df.loc[:,col]=df[col].str.replace(r'\$','',regex=True)
      df.loc[:,col]=df[col].str.replace('--','0.00') # occurs in performance report
      df.loc[:,col]=df[col].str.replace('None','0.00') # occurs in performance report
      df.loc[:,col]=df[col].str.replace(',','').astype(float)
    if col == 'Date':
      df[col] = pd.to_datetime(df[col])

  return df

def read_config():
  '''Reads the config
  
  returns: the config as a dict
  
  raises FileNotFoundError
  '''
  logger=get_logger(__file__)
  fn='dance/data/setup.yaml'
  try:
    with open(fn) as y:
      config=yaml.load(y,yaml.Loader)
  except FileNotFoundError as e:
    raise f'file not found {fn}' from e
  logger.debug('read {} as config'.format(fn))
  return config
