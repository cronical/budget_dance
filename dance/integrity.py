"""Determine the rows in used by iande future that will need to exist in the iande-actl import"""
import pandas as pd

def required_lines(forecast_start_year):
  '''Compute the list of required lines given the forecast start year in form y_year
  Return the required lines and all lines as sets
  '''

  from utility import df_for_table_name
  df=df_for_table_name(table_name='tbl_iande')
  cols= list(df)
  ix=cols.index(forecast_start_year)
  c=cols[ix:]
 
  def not_all_are_empty(a):
    return any([x is not None for x in list(a)])

  must_have=set(df.index[df[c].apply(lambda x: not_all_are_empty(x),axis=1)])

  return must_have, set(df.index)

