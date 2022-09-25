#! /usr/bin/env python
'''
Update the table 'tbl_invest_actl'
'''
import argparse
import os
from dateutil.parser import parse
from openpyxl import load_workbook

from dance.util.books import fresh_sheet, col_attrs_for_sheet,set_col_attrs
from dance.util.files import tsv_to_df, read_config
from dance.util.tables import df_for_table_name, write_table,columns_for_table,conform_table
from dance.util.logs import get_logger
from dance.util.xl_formulas import dyno_fields

logger=get_logger(__file__)
def read_and_prepare_invest_actl(workbook,data_info,table_map=None):
  '''  Read investment actual data from files into a dataframe

  args:
    workbook: name of the workbook (to get the accounts data from)
    data_info: dict that has a value for path used to locate the input file
    table_map: the dict that maps tables to worksheets. Required for the initial setup as it is not yet stored in file

  returns: dataframe with 3 rows per investment (add/wdraw, rlz int/gn, unrlz gn/ls)

  raises:
    FileNotFoundError: if the input file does not exist.
  '''
  input_file=data_info['path']
  try:
    df=tsv_to_df (input_file,skiprows=3)
    logger.info('loaded dataframe from {}'.format(input_file))
  except FileNotFoundError as e:
    raise f'file not found {input_file}' from e
  xfer_file=data_info['path']
  perf_file_prefix=data_info['file_set']['prefix']
  datadir=data_info['file_set']['base_path']

  logger.info('Starting investment actual load')

  # get the account list
  accounts=df_for_table_name(table_name='tbl_accounts',workbook=workbook,table_map=table_map)
  accounts=accounts[accounts.Type == 'I']

  # get the output of the Moneydance report
  df=tsv_to_df (xfer_file,skiprows=3)
  df.dropna(axis=0,how='any',inplace=True)
  df=df.loc[~df.Account.str.contains('TRANSFERS')]
  df=df.groupby('Account').sum() # add the ins and outs
  df=df.mul(-1)# fix the sign
  df.index=df.index.str.strip() # remove leading spaces
  df=df.loc[:,df.columns !='Total'] # drop the total column

  # join these and keep only the data columns using the accounts list as the master
  xfers=accounts.join(df)[df.columns.to_list()]
  xfers.fillna(0, inplace=True) # replace the NaN's (where no transfers occurred) with zeros

  files=os.listdir(datadir)
  files.sort()
  file_cnt=0
  for file_name in files:
    if file_name.find(perf_file_prefix) == 0:
      #grab the year from the file name
      fn_year = file_name.split('.')[0].split('-')[-1]
      perf_file=datadir+file_name
      logger.info('Processing %s',fn_year)
      # now work with the performance data for a year
      df=tsv_to_df (perf_file,skiprows=3)
      # first check to see if the year is valid and its a full year
      orig=[df.columns[x] for x in [1,5]]
      open_close=[parse(x)for x in orig]
      ys=[x.year for x in open_close]
      assert ys[0]==ys[1], 'Report covers more than one year'
      assert 1+(open_close[1]-open_close[0]).days in [365,366], 'Not a full year'
      assert ys[0]==int(fn_year), 'File name year does not equal internal year'
      # change to 'Open' and 'End'
      map={orig[0]:'Open',orig[1]:'End'}
      df.rename(columns=map,inplace=True)

      #get the rows in order
      df.loc[:,'Security']=df['Security'].fillna(value='')
      df=df.loc[df.Security.str.startswith('Total:')] # throw away the securities, just keep the accounts
      df=df.loc[df.Security != 'Total: '] # remove grand total
      df.loc[:,'Security']=df['Security'].str.replace('Total: ','') # just the account names

      # prepare for joins with common index
      df.set_index('Security',inplace=True)
      found=[x in accounts.index.to_list() for x in df.index.to_list()]
      if not all(found):

        print('Not all accounts for %s are in master. Missing:'%fn_year)
        for a in [x for x in df.index.to_list() if x not in accounts.index.to_list()]:
          print('  %s'%a)
        assert all(found)

      # all master accts, and all performance columns
      df=accounts.join(df)[df.columns]
      df.fillna(value=0,inplace=True) # zero out the perf values for accts in master not perf

      # append the transfers
      df=df.join(xfers[fn_year])
      df.rename(columns={fn_year:'Transfers'},inplace=True)
      # compute the two gain fields
      df=df.assign(Realized=lambda x: x.Income + x.Gains) # compute the realized gains
      df=df.assign(Unrealized=lambda x: x.End - (x.Open+x.Transfers+x.Realized))

      # use names in spreadsheet
      map={'Transfers':'Add/Wdraw','Realized':'Rlz Int/Gn','Unrealized':'Unrlz Gn/Ls'}
      df.rename(columns=map,inplace=True)

      # rework so the rows of 3 value types for each account
      rows=df[['Add/Wdraw','Rlz Int/Gn','Unrlz Gn/Ls','Income','Gains']].transpose().stack().reset_index()
      map=dict(zip(rows.columns.to_list(),['ValType','Account','Y'+fn_year]))
      rows.rename(columns=map,inplace=True)
      rows=rows.assign(Key=lambda x: x.ValType + x.Account)
      rows.set_index('Key',inplace=True)
      if file_cnt==0:
        table=rows
      else:
        table=table.join(rows[rows.columns.to_list()[-1]])
      file_cnt=file_cnt+1
    # put the data into the spreadsheet
  wb=load_workbook(filename =workbook)
  table.reset_index(inplace=True) # puts the key back into 1st column
  col_def=columns_for_table(wb,'invest_actl','tbl_invest_actl',read_config())
  table=conform_table(table,col_def['name'])

  return table


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description ='Copies data from input files into tab "invest_actl". ')
  parser.add_argument('--workbook','-w',default='data/test_wb.xlsm',help='Target workbook')# TODO fcast
  parser.add_argument('--path','-p',default= 'invest_x.tsv',help='The path and name of the input file')
  parser.add_argument('--base_path','-b',default= 'data/',help='The base path for the performance reports')
  parser.add_argument('--prefix','-x',default= 'invest-p-',help='The prefix used to locate the performance reports')

  args=parser.parse_args()
  sheet='invest_actl'
  table='tbl_'+sheet
  data=read_and_prepare_invest_actl(workbook=args.workbook,data_info={'path':args.base_path + args.path,
    'file_set':{'base_path':args.base_path,'prefix':args.prefix}})
  table_info=read_config()['sheets'][sheet]['tables'][0]
  data=dyno_fields(table_info,data) # get the taxable status
  wkb = load_workbook(filename = args.workbook, read_only=False, keep_vba=True)
  wkb=fresh_sheet(wkb,sheet)
  wkb= write_table(wkb,target_sheet=sheet,df=data,table_name=table)
  attrs=col_attrs_for_sheet(wkb,sheet,read_config())
  wkb=set_col_attrs(wkb,sheet,attrs)
  wkb.save(args.workbook)
