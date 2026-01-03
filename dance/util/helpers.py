'''helper functions to construct tests'''

import pandas as pd

from dance.util.files import read_config
from dance.util.tables import df_for_table_name

def actual_years():
  '''get the list of actual years as integers and as Y years'''
  config=read_config()
  years=range(config['start_year'],config['first_forecast_year'])
  years=list(years)
  y_years=['Y'+str(y) for y in years]
  return years,y_years

def get_row_set(workbook,table_name,filter_on,index_on,in_list=None,starts_with=None,contains=None):
  '''get a set of rows from table named table_name in the workbook
  filter the rows based on the values in the filter_on being in the inlist.
  
  args:
    workbook - the workbook filename
    table_name - including the tbl_ prefix
    filter_on - either 'index' or a valid column name
    index_on - either 'index' or a valid column name - used to set the result's index
    one of the filter methods

  returns: dataframe with the values from the index_on field as the index
          
  raises: ValueError if caller does not provide exactly one of in_list, starts_with, contains
  '''
  filter_styles=[(in_list is not None),(starts_with is not None),(contains is not None)]
  if sum(filter_styles)!=1:
    raise ValueError('Must include exactly one of in_list, starts_with, contains')
  _,y_years=actual_years()
  df=df_for_table_name(table_name=table_name,data_only=True,workbook=workbook)
  if filter_on=='index':
    filter_values=df.index
  else:
    filter_values=df[filter_on]
  if in_list is not None:
    sel=filter_values.isin(in_list) # only the end balances
  if starts_with is not None:
    sel=filter_values.str.startswith(starts_with)
  if contains is not None:
    sel=filter_values.str.contains(contains,regex=False)
  df=df.loc[sel]
  if index_on!='index':
    df.set_index(index_on,inplace=True)
  df=df[y_years]
  df=df.round(decimals=2)
  return df

def stack_as(df,header):
  '''Take a dataframe with a single index and year columns and stack
  Return: a dataframe with the years added as 2nd index and values under a column named header.'''
  df=pd.DataFrame(df.stack())
  df.rename(columns={0:header},inplace=True)
  df.index.set_names(['Account','Year'],inplace=True)  
  return df

def align(df_list):
  '''Return new dataframe with the single columns of the given dataframes aligned on the index 
  nans are replaced with 0'''
  df=None
  for df_n in df_list:
    if df is None:
      df=df_n
    else:
      df=df.join(df_n,how='outer')
  df.fillna(0, inplace=True)
  return df

