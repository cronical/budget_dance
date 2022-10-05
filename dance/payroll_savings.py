#! /usr/bin/env python
'''Process the payroll to savings records from Moneydance export (report: 401, HSA, ESP payroll data)'''
import warnings
import pandas as pd
from dance.util.logs import get_logger

warnings.simplefilter(action='ignore', category=FutureWarning)

logger=get_logger(__file__)

def payroll_savings():
  '''Get the payroll to savings records from Moneydance export and summarize so data items can be put in spreadsheet
  These data refer to deductions from payroll together with employer contributions into savings vehicles

  Args: None
  
  Returns: 
    a dataframe that discards the inbound and processes the outbound transfers
    So it has one row ('Amount') and multiple y_year columns
    Only has columns where data exists
  '''

  filename='data/payroll_to_savings.tsv'
  df=pd.read_csv(filename,sep='\t',skiprows=3) 
  df.dropna(how='all',inplace=True) # blank rows
  acct=df[['Target Account']].copy()

  acct.fillna(method= 'ffill',inplace=True)#propogate accounts
  df['Target Account']=acct
  df=df.loc[df.Date.notna()] # remove headings and totals
  df['Amount']=df.Amount.astype(float)
  sel=~ (df.Amount > 0) | df.Description.str.contains('return of excess')
  df=df.loc[sel].copy() # remove the transfers in (except for any return of excess)
  df.Amount = - df.Amount # change sign

  # remove refunds to hsa
  sel = ~ df.Description.str.contains('ADJ') 
  df=df.loc[sel].copy()

  col = 'Date'
  df[col] = pd.to_datetime(df[col])

  # create the year field to allow for pivot
  df['Year']=df['Date'].dt.year
  df['Year'] = df['Year'].apply('Y{}'.format)
  summary= df.pivot_table(index='Target Account',values='Amount',columns='Year',aggfunc='sum')
  summary=summary.reset_index()
  summary.rename(columns={'Target Account':'Account'},inplace=True)
  summary.Account=summary.Account.str.strip()
  return summary

if __name__=='__main__':
  payroll_savings()
