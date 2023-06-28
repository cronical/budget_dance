#! /usr/bin/env python
'''
Prepare the data from the Investment IandE report from which is in the file invest-iande.tsv.

'''
import argparse
from openpyxl import load_workbook

import pandas as pd

from dance.util.books import fresh_sheet, col_attrs_for_sheet,set_col_attrs
from dance.util.files import tsv_to_df, read_config
from dance.util.tables import  columns_for_table, write_table,get_f_fcast_year,conform_table
from dance.util.logs import get_logger
from dance.util.xl_formulas import actual_formulas,forecast_formulas,dyno_fields,this_row

logger=get_logger(__file__)

def y_years(col_name):
  '''Given a column name return it unless its a number, in that case prepend "Y".'''
  if isinstance(col_name,str):
    return col_name
  return f'Y{col_name}'

def read_and_prepare_invest_iande(workbook,data_info,f_fcast=None):
  '''  Read investment income and expense actual data from file into a dataframe

  args:
    workbook: name of the workbook (to get the accounts data from)
    data_info: dict that has a value for path used to locate the input file, which contains transaction data for a series of years
    f_fcast: Optional. The first forecast year as Ynnnn. If none, will read from the workbook file. Default None.
    table_map: the dict that maps tables to worksheets. Required for the initial setup as it is not yet stored in file

  returns:  A summarized dataframe which has years for columns, where summed values are.
    It also has columns for the Investment account name and the I and E category.

  raises:
    FileNotFoundError: if the input file does not exist.
  '''
    # get the workbook from file
  try:
    wb = load_workbook(filename = workbook, read_only=False, keep_vba=True)
    logger.info('loaded workbook from {}'.format(workbook))
    config=read_config()
  except FileNotFoundError:
    raise FileNotFoundError(f'file not found {workbook}') from None
  if f_fcast is None:
    f_fcast='Y%d' % get_f_fcast_year(wb,config) # get the first forecast year from the general state table or config as available
  logger.info ('First forecast year is: %s',f_fcast)

  input_file=data_info['path']
  try:
    df=tsv_to_df (input_file,nan_is_zero=False,skiprows=3,string_fields=['Check#','Description','Category','Tags','C'])
    logger.info('loaded dataframe from {}'.format(input_file))
  except FileNotFoundError as e:
    raise f'file not found {input_file}' from e
  df=df.loc[df.Account !='Total'] # remove total line
  df=df.dropna(how='all')# and blank row after total
  df=df[['Account','Date','Category','Amount']]
  df['Year']=df.Date.dt.year
  vals_df=pd.pivot_table(df,index=['Account','Category'],aggfunc='sum',values='Amount',columns='Year')
  vals_df.reset_index(inplace=True) # Account and category are now columns
  full_categories=list(vals_df.Category.str.split(':'))
  vals_df['Category']=[':'.join(a[-2:])for a in full_categories]  # last 2 parts of the category are used
  vals_df.fillna(0,inplace=True) # no missing values - use zeros
  vals_df.insert(loc=2,column='IorE',value=[a[0]for a in full_categories],allow_duplicates=True)# Mark and I, X or T
  vals_df.insert(loc=3,column='Type',value='value',allow_duplicates=True) # Type is value or rate
  vals_df.rename(columns=y_years,inplace=True) # use the y_years format for column names
  rates_df=vals_df.copy(deep=True) # build out the rates rows
  rates_df['Type']='rate'
  ys=rates_df.columns[4:]
  rates_df[ys]='=ratio_to_start({},{},this_col_name())'.format(this_row('Account'),this_row('Category')) # the rates formula
  df=pd.concat([vals_df,rates_df])
  df.reset_index(drop=True,inplace=True) # new clean index
  df.insert(0,column='Key',value=df.Account.map(str)+':'+df.Category.map(str)+':'+df.Type.map(str)) # full key
  df.insert(1,column='Category_Type',value=df.Category.map(str)+':'+df.Type.map(str)) # to select category rates
  
  for y in range(int(f_fcast[1:]),config['end_year']+1): # add columns for forecast years
    df['Y{}'.format(y)]=None
  col_def=columns_for_table(wb,'invest_iande_work','tbl_invest_iande_work',config)
  df=conform_table(df,col_def['name'])
  return df


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description ='Prepares income and expense data to insert into  "tbl_invest_iande_work". ')
  parser.add_argument('--workbook','-w',default='data/test_wb.xlsm',help='Target workbook') # TODO change to fcast.xlsm
  parser.add_argument('--path','-p',default= 'data/invest-iande.tsv',help='The path and name of the input file')

  args=parser.parse_args()
  config=read_config()
  ffy=config['first_forecast_year']
  table_info=config['sheets']['invest_iande_work']['tables'][0]
  data_info=table_info['data']
  data_info['path']=args.path
  data=read_and_prepare_invest_iande(workbook=args.workbook,data_info=data_info)
  data=dyno_fields(table_info,data)
  data=forecast_formulas(table_info,data,ffy) # insert forecast formulas per config
  data=actual_formulas(table_info,data,ffy) # insert actual formulas per config
  sheet='invest_iande_work'
  table='tbl_'+sheet
  wkb = load_workbook(filename = args.workbook, read_only=False, keep_vba=True)
  wkb=fresh_sheet(wkb,sheet)
  wkb= write_table(wkb,target_sheet=sheet,df=data,table_name=table)
  attrs=col_attrs_for_sheet(wkb,sheet,read_config())
  wkb=set_col_attrs(wkb,sheet,attrs)
  wkb.save(args.workbook)

  pass
