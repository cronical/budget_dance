#! /usr/bin/env python
'''
Update the table 'tbl_invest_actl'
'''
import argparse
import os

import pandas as pd
from dateutil.parser import parse
from openpyxl import load_workbook

from dance.other_actls import setup_year
from dance.util.books import col_attrs_for_sheet, fresh_sheet, set_col_attrs
from dance.util.files import read_config, tsv_to_df
from dance.util.logs import get_logger
from dance.util.tables import (columns_for_table, conform_table,
                               df_for_table_name, write_table)
from dance.util.xl_formulas import dyno_fields


logger=get_logger(__file__)

def read_passthru_accts(data_info):
  '''Grab the balances of the pass through accounts from the tsv file indicated in the argument
  
  argument: dictionary with 'path' to locate the file
  returns dataframe with the passthrough account names transformed to the actual account names and and their balances'''

  df=tsv_to_df(data_info['path'],skiprows=3,string_fields=['Account','Notes'])
  df=df.dropna(how='any')
  #strip off the indents
  df=pd.DataFrame([df['Account'].str.strip(),df['Current Balance']]).T # avoids warning A value is trying to be set on a copy of a slice from a DataFrame
  df=df.loc[df.Account.str.startswith('Pass-')]
  df['Account']=df.Account.replace('Pass-','',regex=True)# conform the passthru account names to the main account names
  df['Account']=df.Account.replace('-',' - ',regex=True)

  return df

def read_and_prepare_invest_actl(workbook,data_info,table_map=None):
  '''  Read investment actual data from files into a dataframe

  args:
    workbook: name of the workbook (to get the accounts and fees data from)
    data_info: dict that has a value for path used to locate the input file
    table_map: the dict that maps tables to worksheets. Required for the initial setup as it is not yet stored in file

  returns: dataframe with 5 rows per investment (add/wdraw, rlz int/gn, unrlz gn/ls, Income, Gains)
    The unrealized gain value has the fees removed

  raises:
    FileNotFoundError: if the input file does not exist.
  '''

  logger.info('Starting investment actual load')

  xfer_file=data_info['path']
  perf_file_prefix=data_info['file_set']['prefix']
  datadir=data_info['file_set']['base_path']

  # get the account list
  accounts=df_for_table_name(table_name='tbl_accounts',workbook=workbook,table_map=table_map)
  accounts=accounts[accounts.Type == 'I']

  # get the output of the Moneydance investment transfers report
  try:
    df=tsv_to_df (xfer_file,skiprows=3)
    logger.info('loaded dataframe from {}'.format(xfer_file))
  except FileNotFoundError as e:
    raise f'file not found {xfer_file}' from e
  df.dropna(axis=0,how='any',inplace=True)
  df=df.loc[~df.Account.str.contains('TRANSFERS')]
  df=df.groupby('Account').sum() # add the ins and outs
  df=df.mul(-1)# fix the sign
  df.index=df.index.str.strip() # remove leading spaces
  df=df.loc[:,df.columns !='Total'] # drop the total column

  # join these and keep only the data columns using the accounts list as the master
  xfers=accounts.join(df)[df.columns.to_list()]
  xfers.fillna(0, inplace=True) # replace the NaN's (where no transfers occurred) with zeros

  # get the performance reports' data
  files=os.listdir(datadir)
  files.sort()
  file_cnt=0
  string_fields='Account,Security,Action,Unnamed: 8'.split(',')
  prior_pbals=None
  for file_name in files:
    if file_name=='.DS_Store': # MacOS finder leaves this around if you look at the folder.
      continue
    if perf_file_prefix is None or file_name.startswith(perf_file_prefix):
      #grab the year from the file name
      fn_year = file_name.split('.')[0].split('-')[-1]
      perf_file=datadir+file_name
      logger.info('Processing %s',fn_year)
      #read the internal date and check it.

      
      # now work with the performance data for a year
      df=tsv_to_df (perf_file,skiprows=3,string_fields=string_fields)
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
      df=df.drop(['Buys','Sales','Return %','Annual % (ROI)'],axis=1)# drop some columns we don't care about
      # all master accts, and all performance columns
      df=accounts.join(df)[df.columns]
      df.fillna(value=0,inplace=True) # zero out the perf values for accts in master not perf

      # append the transfers
      df=df.join(xfers[fn_year])
      # get the fees and append as a column
      iiw=pd.read_excel(workbook,sheet_name='invest_iande_work',skiprows=1)
      iiw=iiw.loc[iiw.Category_Type=='Investing:Account Fees:value']
      iiw.set_index('Account',drop=True,inplace=True)
      df=df.join(iiw['Y'+fn_year],how='left').fillna(value=0)
      df.rename(columns={'Return Amount': 'Return_Amount',fn_year:'Transfers','Y'+fn_year:'Fees'},inplace=True)

      # get the pending re-investments from the Merrill IRA
      retro=['IRA - VEC - ML'] # the pending only makes sense for accounts where the outgoing $ comes back as securities - i.e. this Merrill account
      pbals=read_passthru_accts({'path':'./data/acct-bals/'+file_name}) # TODO locate path via config.
      pbals=pbals.loc[pbals.Account.isin(retro)].copy()
      pbals.set_index('Account',inplace=True)# same index for the join
      pbals.rename({'Current Balance':'Pending'},axis=1,inplace=True)# convenient column name
      df=df.join(pbals,how='left').fillna(value=0) # df now has pending column
      if prior_pbals is not None:
        df=df.join(prior_pbals,how='left').fillna(value=0) # df now has prior column
      else:
        df['Prior']=0
      prior_pbals=pbals.copy() # for next year
      prior_pbals.rename({'Pending':'Prior'},axis=1,inplace=True)# convenient column name
      

      # compute the two gain fields
      df=df.assign(Realized=lambda x: x.Income + x.Gains) # compute the realized gains
      df=df.assign(Unrealized=lambda x: (x.Return_Amount+x.Fees- (df.Pending - df.Prior)) - x.Realized)# unrealized is a plug so fees are included

      df['Check']=df.Open + df.Transfers + df.Realized + df.Unrealized 
      df['Delta']=df.End - df.Check
      valid= (df.End-df.Check).abs() < .001
      if ~valid.all():
        logger.error('We have a problem getting the end balances. File = {}'.format(file_name))
        print(df.loc[~valid])
        print('''
        Things to look at
        - Merrill (IRA) reinvestment rounding problems - off by 1 or 2 cents.
          - Export Transfers, Detailed report and run dance.util.match_retro.py to locate
        - Unit prices - not same precision 
          - At price history don't take the printed unit value - recalculate as ratio for 12/31/yy price on items that are off
        - Income items not marked as MiscInc 
          - such as interest being coded as xfr
          - remember to re-run/save performance report
        - Transfers that do not pass through a bank (or items in the transfers report used to generate the invest_x.tsv file)
        - The Transfers, Detailed report for just the account and year can be helpful.
        ...''')
        assert False
      else:
        logger.info('Investment balance checks OK for {}'.format(file_name))
      # use names in spreadsheet
      map={'Transfers':'Add/Wdraw','Realized':'Rlz Int/Gn','Unrealized':'Unrlz Gn/Ls'}
      df.rename(columns=map,inplace=True)

      # rework so the rows of 5 value types for each account
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

def get_cap_gains(data_info):
  '''Get cap gains'''
  txt_fields=['Account', 'Security', 'Action','Unnamed: 8']
  df=tsv_to_df (data_info['path'],skiprows=3,string_fields=txt_fields)
  df['Account'].fillna(method='ffill',inplace=True)
  df['Security'].fillna(method='ffill',inplace=True)
  df=df.loc[~pd.isnull(df.Action)]
  df=df.loc[~df['Action'].str.startswith('Total:')]
  if False:
    #create Duration column and populate Action column for duration rows
    durations=['Long Term','Short Term','Unrealized']
    for _,row in   df.iterrows():
      action=row['Action']
      if action.startswith('Sell') or action=='Unrealized':
        share_info=row['Unnamed: 8']
        share_info=parse_share_info(share_info)
        block=df.loc[(df.Account==row['Account']) & (df.Date==row['Date']) & (df.Action.isin(durations[:-1]))]
        pass
        for iy,row2 in block.iterrows():
          duration=row2['Action']
          assert duration in durations, 'Expecting Short Term, Long Term, or Unrealized for the action, got: ' + duration
          assert row2['Shares']>=0, 'eh? negative shares'
          if share_info:
            assert row2['Shares']<=share_info[duration],'Inconsistent information for shares/action'
          df.at[iy,'Duration']=duration
          real={'Sell':'Realized','SellXfr':'Realized','Unrealized':'Unrealized'}[action]
          df.at[iy,'Realized']=real # copy the main records action to the block record so its on the same row as the duration
          # the main action row will have a nan in the Realized column. 
          # and thus won't be included in the summary, since its accounted for on the block record with the duration
  del df['Unnamed: 8']
  df=setup_year(df)
  #df1=df.loc[~pd.isnull(df.Duration)]
  df.loc[df.Action=='SellXfr','Action']='Sell'
  df.loc[df.Action=='Sell','Action']='Realized'
  df=df.loc[~df.Action.str.endswith('Term')]
  summary=df.pivot_table(index=['Account'],aggfunc='sum',values='Gains',columns=['Action','Year']) 
  pass
  # Notes:
  #  return amount column on Investment Performance seems to include unrealized, realized and income
  #  average cost method seems to return non sensical results for unrealized
  #   with possible exception when entire lot is sold - like in BKG - JNT - ML
  


  return summary

def parse_share_info(share_info):
  result=None
  if not pd.isna(share_info):
    share_info=share_info.split(':')[-1].strip()
    share_info=share_info.replace(' = ','=')
    share_info=share_info.replace('  ',' ')
    result={}
    for trm in share_info.split(' '):
      dur,shrs=trm.split('=')
      dur={'LT':'Long Term','ST':'Short Term'}[dur]
      shrs=float(shrs.replace(',',''))
      result[dur]=shrs
  return result

if __name__ == '__main__':
  if False:
    get_cap_gains(data_info={'path':'data/cap-gains.tsv'})
  else:
    parser = argparse.ArgumentParser(description ='Copies data from input files into tab "invest_actl". ')
    parser.add_argument('--workbook','-w',default='data/test_wb.xlsm',help='Target workbook')# TODO fcast
    parser.add_argument('--path','-p',default= 'data/invest-x.tsv',help='The path and name of the input file')
    parser.add_argument('--base_path','-b',default= 'data/invest-p/',help='The base path for the performance reports')
    parser.add_argument('--prefix','-x',help='The prefix used to locate the performance reports')

    args=parser.parse_args()
    sheet='invest_actl'
    table='tbl_'+sheet
    data=read_and_prepare_invest_actl(workbook=args.workbook,data_info={'path': os.getcwd()+'/'+args.path,
      'file_set':{'base_path':args.base_path,'prefix':args.prefix}})
    table_info=read_config()['sheets'][sheet]['tables'][0]
    data=dyno_fields(table_info,data) # get the taxable status
    wkb = load_workbook(filename = args.workbook, read_only=False, keep_vba=True)
    wkb=fresh_sheet(wkb,sheet)
    wkb= write_table(wkb,target_sheet=sheet,df=data,table_name=table)
    attrs=col_attrs_for_sheet(wkb,sheet,read_config())
    wkb=set_col_attrs(wkb,sheet,attrs)
    wkb.save(args.workbook)
