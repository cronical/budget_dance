#! /usr/bin/env python
'''Converts extracts from Moneydance bank and credit card balances to a dataframe of changes

Source files are stored as .tsv under the data folder with a name 'bank-bal-<year>'
The logic is to take the year on year delta (less the interest)
'''

import os
import pandas as pd
from dance.util.tables import df_for_table_name


def bank_cc_changes():
  '''Reads the data files available in the data folder and returns a dataframe with the changes in account values

  Source files are stored as .tsv under the data folder with a name 'bank-bal-<year>'
  The logic is to take the year on year delta (less the interest)
  '''

  datadir='./data/'
  files=os.listdir(datadir)
  files.sort()
  data=[[],[]]
  cols=[]
  tot=' - Total'
  rows=['Bank Accounts','Credit Cards']
  inrows=[rows[x] + tot for x in range(0,len(rows))]
  for file_name in files:
    if file_name.find('bank-bal') == 0:
      #grab the year from the file name
      y_year = 'Y' + file_name.split('.')[0].split('-')[-1]
      df=pd.read_csv(datadir+file_name,sep='\t',skiprows=3)
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

  #for cix in range(1,len(cols)):
  #  changes[cols[cix]]=balances.apply(lambda x: x[cols[cix]] - x[cols[cix-1]], axis = 1)

  for cix,col_name in enumerate(cols):
    if cix >0:
      changes[col_name]= balances[col_name]-last_col
    last_col=balances[col_name]

  changes.insert(loc=0,column='Account',value=rows)
  changes.insert(loc=0,column='key',value=rows)
  changes.set_index('key',inplace=True)

  # So far we have the change in account value, but part of that comes from bank interest
  # so remove those amounts.
  # and while we are in here credit cards need a change of sign
  iande_actl=df_for_table_name('tbl_iande_actl')
  cols=changes.columns[1:] # the year numbers
  for col in cols:
    adj=changes.loc['Bank Accounts',col]-iande_actl.loc['Income:I:Invest income:Int:Bank',col]
    changes.loc['Bank Accounts',col]=adj
    changes.loc['Credit Cards',col]=-changes.loc['Credit Cards',col]

  return changes

def main():
  '''If called from the command line prints result'''
  changes= bank_cc_changes()
  print(changes)

if __name__ == '__main__':
  main()
