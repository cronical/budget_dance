'''DataFrame utilities'''

import pandas as pd


from dance.util.logs import get_logger

def tsv_to_df(filename,sep='\t',skiprows=0):
  '''Grab the data from a Moneydance report and return a Pandas DataFrame.

  Typically the file has tab separated fields.

  Args:
    filename: The name of the file to read.
    sep: The field separator, default is tab.
    skiprows: the number of rows to skip at the start of the file.  Default is 0.

  Returns: A data frame with numbers converted to floats and dates as datetime.

  '''
  logger=get_logger(__file__)
  try:
    df=pd.read_csv(filename,sep=sep,skiprows=skiprows,dtype='str') # keep as string because there are some clean ups needed
  except FileNotFoundError:
    logger.error('No file "{}". Quitting.'.format(filename))
    quit()
  cols=df.columns
  for col in cols[1:]:
    if col != 'Date' and col != 'Notes':
      df.loc[:,col]=df[col].fillna(value='0.00')
      df.loc[:,col]=df[col].str.replace(r'\$','',regex=True)
      df.loc[:,col]=df[col].str.replace('--','0.00') # occurs in performance report
      df.loc[:,col]=df[col].str.replace('None','0.00') # occurs in performance report
      df.loc[:,col]=df[col].str.replace(',','').astype(float)
    if col == 'Date':
      df[col] = pd.to_datetime(df[col])

  return df


def get_val(frame, line_key ,  col_name):
  '''get a single value from a dataframe'''
  return frame.loc[line_key,col_name]

def put_val(frame, line_key ,  col_name, value):
  '''Put a single value into a dataframe'''
  frame.loc[line_key,col_name]=value





