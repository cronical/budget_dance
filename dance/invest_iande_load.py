#! /usr/bin/env python
'''
Prepare the data from the Investment IandE report from which is in the file invest-iande.tsv.

'''
import argparse
from openpyxl import load_workbook

import pandas as pd

from dance.util.books import fresh_sheet, col_attrs_for_sheet,set_col_attrs
from dance.util.files import tsv_to_df, read_config
from dance.util.tables import  write_table,this_row
from dance.util.logs import get_logger

logger=get_logger(__file__)

def y_years(col_name):
  '''Given a column name return it unless its a number, in that case prepend "Y".'''
  if isinstance(col_name,str):
    return col_name
  return f'Y{col_name}'

def read_and_prepare_invest_iande(data_info):
  '''  Read investment income and expense actual data from file into a dataframe

  args:
    workbook: name of the workbook (to get the accounts data from)
    data_info: dict that has a value for path used to locate the input file, which contains transaction data for a series of years
    table_map: the dict that maps tables to worksheets. Required for the initial setup as it is not yet stored in file

  returns:  A summarized dataframe which has years for columns, where summed values are.
    It also has columns for the Investment account name and the I and E category.

  raises:
    FileNotFoundError: if the input file does not exist.
  '''
  input_file=data_info['path']
  try:
    df=tsv_to_df (input_file,nan_is_zero=False,skiprows=3,string_fields=['Check#','Description','Category','Tags','C'])
    logger.info('loaded dataframe from {}'.format(input_file))
  except FileNotFoundError as e:
    raise f'file not found {input_file}' from e
  df=df.loc[df.Account !='Total'] # remove total line
  df=df.dropna(how='all')# and blank row after total
  df=df[['Account','Date','Category','Amount']]
  # last 2 parts of the category are used
  df['Short_cat']=[':'.join(a[-2:])for a in list(df.Category.str.split(':'))]
  df['Year']=df.Date.dt.year
  vals_df=pd.pivot_table(df,index=['Account','Short_cat'],aggfunc='sum',values='Amount',columns='Year')
  vals_df.reset_index(inplace=True)
  vals_df.fillna(0,inplace=True)
  vals_df.rename(columns={'Short_cat':'Category'},inplace=True)
  vals_df.insert(loc=2,column='Type',value='value',allow_duplicates=True)
  vals_df.rename(columns=y_years,inplace=True)
  rates_df=vals_df.copy(deep=True)
  rates_df['Type']='rate'
  ys=rates_df.columns[3:]
  rates_df[ys]='=ratio_to_start({},{},this_col_name())'.format(this_row('Account'),this_row('Category'))
  df=pd.concat([vals_df,rates_df])
  df.insert(0,column='Key',value=df.Account.map(str)+':'+df.Category.map(str)+':'+df.Type.map(str))
  pass
  return df


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description ='Prepares income and expense data to insert into  "tbl_invest_iande_work". ')
  parser.add_argument('--workbook','-w',default='data/test_wb.xlsm',help='Target workbook') # TODO change to fcast.xlsm
  parser.add_argument('--path','-p',default= 'data/invest-iande.tsv',help='The path and name of the input file')
  
  args=parser.parse_args()
  invest_iande_actl=read_and_prepare_invest_iande(data_info={'path': args.path})
  sheet='invest_iande_work'
  table='tbl_'+sheet
  wkb = load_workbook(filename = args.workbook, read_only=False, keep_vba=True)
  wkb=fresh_sheet(wkb,sheet)
  wkb= write_table(wkb,target_sheet=sheet,df=invest_iande_actl,table_name=table)
  attrs=col_attrs_for_sheet(wkb,sheet,read_config())
  wkb=set_col_attrs(wkb,sheet,attrs)
  wkb.save(args.workbook)

  pass
