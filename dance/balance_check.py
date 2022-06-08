#! /usr/bin/env python

"""Given a year compare the values in fcast.xlsm and '<year> Account Balances.tsv'

After a bit of fiddling to get the accounts to match, does a left join
and prints out how closely the values match
"""

  # utility to compare the balances between moneydance account balances report and fcast.xlsm
import argparse
import pandas as pd
from utility import tsv_to_df, df_for_table_name

def compare(year):
  """
  reads the values for a year from a saved the Account Balances report \
    generated by Moneydance and matches to those to the values from fcast.xlsm
  """
  y_year='Y{}'.format(year)
  file_name='data/{} Account Balances.tsv'.format(year)
  fbal=df_for_table_name(table_name='tbl_balances',data_only=True)
  mbal=tsv_to_df(file_name,skiprows=3)
  mbal=mbal.dropna(how='any') # remove rows containing nan
  # this removes account type headings and unresolved transactions missing an account 
  col='Account'
  # select only totals
  mbal=mbal.loc[ mbal[col].str.contains(' - Total') ]
  mbal.loc[:,col]=mbal[col].str.replace(' - Total','') # remove the total label
  mbal=mbal[[col,"Current Balance"]]
  #loan and liabilities have section labels identical to first level of account name, so drop them
  mbal.drop_duplicates(inplace=True)
  mbal.rename(columns={'Current Balance':'Moneydance'},inplace=True)
  mbal.set_index(col,inplace=True)

  fbal=fbal.loc[fbal["ValType"].str.contains("End Bal")] # only the end balances
  fbal=fbal[['AcctName', y_year]]
  fbal.set_index('AcctName',inplace=True)

  jbal=fbal.join(mbal,how='left')
  jbal.fillna(0, inplace=True)
  jbal['delta'] = jbal[y_year] -jbal["Moneydance"]
  jbal.round(decimals=2)
  pd.set_option('display.float_format', lambda x: '%.2f' % x)
  print ("\nExact matches: ".upper())
  print (jbal.loc[abs(jbal.delta) < .005 ])
  print ("\nNot matching: ".upper())
  print (jbal.loc[abs(jbal.delta) >= .005 ])


if __name__ == "__main__":
  # execute only if run as a script
  parser = argparse.ArgumentParser(description ="This program reads the values from a saved the Account Balances report \
    generated by Moneydance and matches to those to the values from fcast.xlsm.")
  parser.add_argument('year', help='provide the 4 digit year',type=int)
  args=parser.parse_args()
  compare(args.year)
