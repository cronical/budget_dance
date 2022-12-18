#! /usr/bin/env python

'''Given a year compare the values in fcast.xlsm and '<year> Account Balances.tsv'

After a bit of fiddling to get the accounts to match, does a left join
and prints out how closely the values match
'''

  # utility to compare the balances between moneydance account balances report and fcast.xlsm
import argparse

import os

from dance.util.files import tsv_to_df,read_config
from dance.util.tables import df_for_table_name
from tests.helpers import actual_years, align,  get_row_set, stack_as


def md_balances(workbook='data/test_wb.xlsm'):
  '''Get the moneydance actual balances from the balance files that match to the accounts

  returns: a DataFrame with the index as the account name.
  '''
  years,_=actual_years()
  base_path=read_config()['sheets']['transfers_actl']['tables'][0]['data']['file_sets']['balances']
  files=list(set(os.listdir(base_path))-set(['.DS_Store']))
  files.sort()
  df=df_for_table_name('tbl_accounts',workbook=workbook)
  df=df.drop(columns=df.columns)# just want the index
  for file_name in files:
    yr=file_name.split('.')[0]
    if int(yr) not in years:
      continue
    m_bal=tsv_to_df(base_path+file_name,skiprows=3)
    m_bal=m_bal.dropna(how='any') # remove rows containing nan
    # this removes account type headings and unresolved transactions missing an account
    col='Account'
    # select only totals
    m_bal=m_bal.loc[ m_bal[col].str.contains(' - Total') ]
    m_bal.loc[:,col]=m_bal[col].str.replace(' - Total','') # remove the total label
    m_bal=m_bal[[col,'Current Balance']]
    #loan and liabilities have section labels identical to first level of account name, so drop them
    m_bal.drop_duplicates(inplace=True)
    m_bal.rename(columns={'Current Balance':'Y'+yr},inplace=True)
    m_bal.set_index(col,inplace=True)
    df=df.join(m_bal,how='left')
  return df

def balance_test_pairs(workbook):
  '''
  get a dataframe with expected and found values for actual balances
  index is (Account,Year)
  '''
  md_bal=md_balances(workbook) 
  md_bal=stack_as(md_bal,'Balance tsv files')

  w_bal=get_row_set(workbook=workbook,table_name='tbl_balances',filter_on='ValType',in_list=['End Bal'],index_on='AcctName')
  w_bal=stack_as(w_bal,'Balances[EndBal]')

  joined_bal=align([md_bal,w_bal])

  return joined_bal

if __name__ == '__main__':
  # execute only if run as a script
  parser = argparse.ArgumentParser(description ='This program reads the values from a saved the Account Balances report \
    generated by Moneydance and matches to those to the values from fcast.xlsm.')
  parser.add_argument('-workbook',default='data/test_wb.xlsm',help='provide an alternative workbook')
  args=parser.parse_args()
  df=balance_test_pairs(args.workbook)
  zeros=df.diff(axis=1)[df.columns[1]]==0
  msg='%d out of %d balances matched'%(zeros.sum(),len(zeros))
  print(msg)