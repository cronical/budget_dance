#! /usr/bin/env python
'''Process the ira distribution records from Moneydance export'''
import pandas as pd
from openpyxl.utils.cell import range_boundaries
from dance.util.logs import get_logger
from dance.util.tables import  df_for_table_name_for_update

logger=get_logger(__file__)

def ira_distr_summary():
  '''Get the ira distribution records from Moneydance export and summarize so data items can be put in spreadsheet
  These data refer to distributions from accounts that are internal to Moneydance (typical). 

  Args: None
  
  Returns: 
    a dataframe that adds the inbound and outbound transfers together
    So it has one row ('Amount') and multiple y_year columns
    Only has columns where data exists
  '''

  filename='data/IRA-Distr.tsv'
  df=pd.read_csv(filename,sep='\t',skiprows=3) #,index_col=0)
  df.dropna(how='all',inplace=True)
  df=df[~df['Account'].str.contains('Total')] # remove totals
  df.fillna(0, inplace=True) # replace the NaN's with zeros
  cols=df.columns
  for col in cols[1:]:
    if col == 'Amount':
      df.loc[:,col]=df[col].str.replace(r'\$','',regex=True)
      df.loc[:,col]=df[col].str.replace(',','').astype(float)
    if col == 'Date':
      df[col] = pd.to_datetime(df[col])
  #remove the negatives, which are the transfers out of the IRA account
  #that way the totals will be the sum of the taxes and the postive amount transfered to the bank
  df=df[df.Amount>0]

  # create the year field to allow for pivot
  df['Year']=df['Date'].dt.year
  df['Year'] = df['Year'].apply('Y{}'.format)
  summary= df.pivot_table(values='Amount',columns='Year',aggfunc='sum')
  return summary
