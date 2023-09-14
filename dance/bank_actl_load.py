#! /usr/bin/env python
'''Converts extracts from Moneydance bank and credit card balances to a dataframe of changes

Source files are stored as .tsv under the data folder with a name 'acct-bals-<year>'
The logic is to take the year on year delta (less the interest)
'''
import os

import pandas as pd

from dance.util.files import read_config
from dance.util.tables import df_for_table_name

config=read_config()

def bank_cc_changes(data_info,target_file,table_map=None):
  '''Reads the account data files available in the data folder, combines them and produces the net change due to transfers per year.
  Source files are stored as .tsv under the data folder with a name 'acct-bal-<year>'
  The logic is to take the year on year delta (less the interest)

  args:
    data_info: dictionary containing the base_path
    target_file: the workbook that contains the iande sheet.  This is read to get the interest values, which are removed from the result.
    table_map: a dict to locate the iande sheet when file is being constructed.
  returns: a dataframe with the changes in account values due to transfers

  '''
  ffy=config['first_forecast_year']
  base_path=data_info['file_sets']['balances']
  files=os.listdir(base_path)
  files=list(set(files)-set(['.DS_Store']))
  files.sort()
  data=[[],[]]
  cols=[]
  tot=' - Total'
  rows=['Bank Accounts','Credit Cards']
  inrows=[rows[x] + tot for x in range(0,len(rows))]
  for file_name in files:
    y=file_name.split('.')[0]
    if not y.isnumeric():
      raise ValueError('File %s in %s should have a numeric file name'%(y,base_path))
    #grab the year from the file name
    y_year = 'Y' + y
    if ffy <= int(y): # only up to the configured first forecast year less one
      continue
    df=pd.read_csv(base_path+file_name,sep='\t',skiprows=3)
    # move the account to the index
    df.set_index('Account',inplace=True)
    #only remaining column is our data
    column = df.columns[0]
    df.loc[:,column]=df[column].str.replace(r'\$','',regex=True)
    df.loc[:,column]=df[column].str.replace(',','').astype(float)

    data[0].append(df.loc[inrows[0],column])
    data[1].append(df.loc[inrows[1],column])
    cols.append(y_year)

  balances=pd.DataFrame(data,index=rows,columns=cols)
  
  changes=pd.DataFrame(index=rows)

  for cix,col_name in enumerate(cols):
    if cix >0:
      changes[col_name]= balances[col_name]-last_col
    last_col=balances[col_name]

  # So far we have the change in account value, but part of that comes from bank interest
  # so remove those amounts.

  iande=df_for_table_name('tbl_iande',workbook=target_file,table_map=table_map)
  cols=changes.columns # the year numbers
  for col in cols:
    adj=changes.loc['Bank Accounts',col]-iande.loc['Income:I:Invest income:Int:Bank',col]
    changes.loc['Bank Accounts',col]=adj

  # and fix the sign
  # changes=changes.mul(-1)

  return changes

def main():
  '''If called from the command line prints result'''
  changes= bank_cc_changes(data_info={'file_sets':{'balances':'./data/acct-bals/'}},
                           target_file=config['workbook'])
  print(changes)

if __name__ == '__main__':
  main()
