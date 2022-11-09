'''Utility to match the IRA - VEC - ML "retro" transactions given an input file
This is to locate the inevitable (it appears) problems - usually off by one cent.
This finds the "Reinvestment Share(s)" lines and the "Reinvestment Program" lines and matches them on date and amount
The input file is the output of "Transfers, Detailed" for the year in question, for the source account, above and the target account being
all bank, all liability, all income and all expense.
'''
import argparse

from numpy import negative
import pandas as pd

from dance.util.files import tsv_to_df

def main():
  parser=argparse.ArgumentParser()
  parser.add_argument('file')
  args=parser.parse_args()
  df=tsv_to_df(args.file,skiprows=3,string_fields=['Target Acount','Source Account','Description'])
  df=df.loc[~pd.isnull(df.Description)]
  shares=df.loc[df.Description.str.startswith('Reinvestment Share(s):')].drop(['Target Account'],axis=1)
  program=df.loc[df.Description.str.startswith('Reinvestment Program')].drop(['Target Account'],axis=1)
  program.loc[:,'Amount']=program.Amount.apply(negative)
  shares.set_index(['Date','Amount'],inplace=True)
  program.set_index(['Date','Amount'],inplace=True)
  oj=program.join(shares,how='outer',lsuffix='_shares',rsuffix='_program')
  review=oj.loc[pd.isnull(oj)[['Description_shares','Description_program']].any(axis=1)]
  print(review)
  pass

if __name__=='__main__':
  main()
  