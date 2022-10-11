#! /usr/bin/env python
'''Process the payroll to savings records from Moneydance export (report: 401, HSA, ESP payroll data)'''
import warnings
import pandas as pd
from dance.util.files import tsv_to_df
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

  filename='data/payroll_to_savings.tsv'  # TODO move to argument
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

  df=setup_year(df)  # create the year field to allow for pivot
  summary= df.pivot_table(index='Target Account',values='Amount',columns='Year',aggfunc='sum')
  summary=summary.reset_index()
  summary.rename(columns={'Target Account':'Account'},inplace=True)
  summary.Account=summary.Account.str.strip()
  return summary

def IRA_distr():
  '''Get the IRA distribution records from Moneydance export and summarize so data items can be put in spreadsheet
  These data refer to IRA distributions and the related tax withholding

  Args: None
  
  Returns: 
    a dataframe with categories or accounts as rows and multiple y_year columns
    Categories are the income distribution category (as positive)
    The only account is 'Bank Accounts'
    Bank accounts and withholder numbers are stated as negatives
    Only has columns where data exists
  '''  
  filename='data/IRA-Distr.tsv'  # TODO move to argument
  df=tsv_to_df(filename,skiprows=3,string_fields='Account,Category,Description,Tags,C'.split(','))
  df.dropna(how='any',inplace=True) # total and blank rows
  df=setup_year(df)
  summary=df.pivot_table(index='Category',values='Amount',columns='Year',aggfunc='sum')
  summary.fillna(value=0,inplace=True)
  summary=summary.reset_index()
  summary=summary.loc[~summary.Category.str.startswith('IRA')]
  distr_sel=summary.Category.str.endswith('IRA-Txbl-Distr')
  distr_cat='Income:'+summary.loc[distr_sel,'Category'].squeeze()
  ofid_cat='Expenses:Y:Outside Flows:IRA Distr'
  tx=summary.Category.str.endswith('IRA WH')
  wh=summary.loc[tx].copy()
  wh['Category']='Expenses:'+wh['Category']
  distr=summary.drop('Category',axis=1).loc[~tx]
  # compute the distribution from the bank portion and the witholding portion for distributions that are sourced from an account in MD
  banks= distr.loc[~distr_sel].sum()
  borw=banks+wh.drop('Category',axis=1).sum()
  distr=distr.loc[distr_sel].sum()
  distr2=-borw.drop([c for c in banks.index if banks[c]==0])
  distr.update(distr2)
  distr=pd.concat([pd.Series(data=[distr_cat],index=['Category']),distr])
  banks=pd.concat([pd.Series(data=['Bank Accounts'],index=['Category']),banks])
  distr=pd.DataFrame(distr).T
  banks=pd.DataFrame(banks).T
  summary=pd.concat([distr,banks,wh])
  ofid=summary.drop('Category',axis=1).sum()
  ofid=pd.concat([pd.Series(data=[ofid_cat],index=['Category']),ofid])
  ofid=pd.DataFrame(ofid).T 
  summary=pd.concat([summary,ofid])
  summary.reset_index(drop=True,inplace=True)
  return summary

def hsa_disbursements():
  '''Get the HSA disbursement records from Moneydance export and summarize so data items can be put in spreadsheet
  These data refer to medical payments made from HSA accounts

  Args: None
  
  Returns: 
    a dataframe with HSA disbursements by year
    Only has columns where data exists
  ''' 
  filename='data/HSA - disbursements.tsv'# TODO move to argument
  df=tsv_to_df(filename,skiprows=3,string_fields='Target Account,Source Account,Description,Memo'.split(','))
  df.dropna(how='all',inplace=True) # blank rows
  acct=df[['Target Account']].copy()
  acct.fillna(method= 'ffill',inplace=True)#propogate accounts
  df['Target Account']=acct
  df=df.loc[df.Date.notna()] # remove headings and totals
  dropthese=['EXCESS CONTRIBUTION','INCENTIVE AWARD','INVESTMENT PURCHASE','Investment Purchase','INDIVIDUAL CONTR','EMPLOYER CONTR','HSA Video Credit','PARTIC CONTR','TRV - GBD']
  rgx='(' + '|'.join(dropthese) + ')'
  sel=~ df['Description'].str.contains(rgx,regex=True)
  df=df.loc[sel]
  df=setup_year(df)  # create the year field to allow for pivot
  summary= df.pivot_table(index='Target Account',values='Amount',columns='Year',aggfunc='sum')
  summary=summary.reset_index()
  summary.rename(columns={'Target Account':'Account'},inplace=True)
  summary.Account=summary.Account.str.strip()
  return summary


def setup_year(df):
  '''Convert the date field and create a year field, returning revised dataframe'''
  df['Year']=df['Date'].dt.year.astype(int)
  df['Year'] = df['Year'].apply('Y{}'.format)
  return df

if __name__=='__main__':
  # payroll_savings()
  # IRA_distr()
  hsa_disbursements()
