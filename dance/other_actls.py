#! /usr/bin/env python
'''Process the payroll to savings records from Moneydance export (report: 401, HSA, ESP payroll data)'''
import warnings
from os.path import exists

import pandas as pd

from dance.util.files import tsv_to_df
from dance.util.logs import get_logger

warnings.simplefilter(action='ignore', category=FutureWarning)

logger=get_logger(__file__)

def sel_inv_transfers_original(): # TODO delete this 
  '''Get amounts transferred to/from certain brokerages, mutual funds, loans from/to any banks.
  Use of passthru can hide the other half of the transaction.
  This finds the matching transaction in passthru to determine the other side.
  After that income and expense categories are removed before summing.

  Assumptions:
    Brokerages must be named starting with BKG (to know that shares need to be parsed)
    Files are tab separated text files named based on the account name without spaces as data/trans_acct.tsv
    List all accounts that could have transactions - will ignore if no file found.

  arguments: None # TODO pass the file info in
  returns: dataframe with investment accounts for rows and years for columns
    positive values indicate amount moved out of bank into savings/investment

  '''

  pass_cats=['Passthru']
  sel_inv_accts='BKG - JNT - ML,BKG - JNT - Vanguard,BKG - JNT - CP1,BND - GBD - TRY,BND - VEC - TRY,LON - JNT - HED,MUT - JNT - T Rowe Price'.split(',')
  pass_files=['data/trans_' + cat+'.tsv' for cat in pass_cats]
  sel_files=['data/trans_' + sia.replace(' ','') +'.tsv' for sia in sel_inv_accts]
  txt_flds='Account,Check#,Description,Category,Tags,C'.split(',')
  keep_fields='Account,Date,Description,Category,Amount'.split(',')
  df_pass=pd.DataFrame()
  for file in pass_files:
    df_p=tsv_to_df(file,skiprows=3,string_fields=txt_flds)
    df_p=df_p.loc[~df_p.Account.isnull()]
    df_p=df_p.loc[df_p.Account != 'Total']
    df_p=df_p[keep_fields]
    df_pass=pd.concat([df_pass,df_p])
  df_pass=df_pass.reset_index(drop=True)
  df=pd.DataFrame()
  for file in sel_files:
    if exists(file):
      is_bkg=file.find('BKG')!=-1
      df_b=tsv_to_df(file,skiprows=3,string_fields=txt_flds,parse_shares=is_bkg)
      df_b=df_b.loc[~df_b.Account.isnull()]
      if 'Unit' in df_b.columns:
        df_b=df_b.loc[df_b.Unit != 'Shares']
      df_b=df_b.loc[df_b.Account != 'Total']
      # remove the income and expense items. 
      #df_b=df_b.loc[~df_b['Category'].str[:2].isin(['I:','X:','T:'])]
      df=pd.concat([df,df_b])
  df=df.reset_index(drop=True)
  df=df[keep_fields]
  df=setup_year(df)
  # merge_asof almost worked but seems to have a bug yielding nans when a match should have occurred
  # test=pd.merge_asof(df,df_pass,on='Date',by='Amount')
  # the following matches on amount the takes the lowest difference between dates
  for ix,rw in df.loc[df.Category.isin(pass_cats)].iterrows():
    sel=df_pass.Amount==rw.Amount
    if sel.sum()!=0:
      pf=df_pass.loc[sel,['Date','Category']]
      diff=(pf['Date']-rw.Date).abs()
      if pd.Timedelta('8 days')>diff.min():
        # print(diff.min())
        iy=pf.index[list(diff).index(diff.min())]
        df.at[ix,'Category']=pf.loc[iy,'Category']
  # remove the expense items. 
  df=df.loc[~df['Category'].str[:2].isin(['X:','T:'])]
  # and the income unless no reinvestment
  sel= df['Category'].str[:2].isin(['I:'])
  sel = sel  & ~ (df.Account=='LON - JNT - HED')
  df=df.loc[~sel]
  # Also remove passthru assuming it occurs because of a split (presumably to income and/or expense items)
  df=df.loc[df['Category']!='Passthru']
  df.fillna(value='',inplace=True) # category has nans
  sec_start=[a+':' for a in sel_inv_accts]
  sel=False
  for beg in sec_start:
    sel= sel | (df.Category.str.startswith(beg))# remove securities
  df=df.loc[~sel]
  suma= df.pivot_table(index='Account',values='Amount',columns='Year',aggfunc='sum').reset_index()
  return suma

def payroll_savings(data_info):
  '''Get the payroll to savings records from Moneydance export and summarize so data items can be put in spreadsheet
  These data refer to deductions from payroll together with employer contributions into savings vehicles

  Args: 
    data_info: dict that has a value for path used to locate the input file    
  
  Returns: 
    a dataframe that discards the inbound and processes the outbound transfers
    So it has one row ('Amount') and multiple y_year columns
    Only has columns where data exists
  '''

  filename=data_info['path']
  df=pd.read_csv(filename,sep='\t',skiprows=3) 
  df.dropna(how='all',inplace=True) # blank rows
  acct=df[['Target Account']].copy()
  acct.fillna(method= 'ffill',inplace=True)#propogate accounts
  df['Target Account']=acct
  df=df.loc[df.Date.notna()] # remove headings and totals
  df['Amount']=df.Amount.astype(float)
  col = 'Date'
  df[col] = pd.to_datetime(df[col])
  df=setup_year(df)  # create the year field to allow for pivot
  sel= (df.Amount > 0) != (df.Description.str.upper().str.contains('EXCESS')) # remove payments but not return of excess
  df=df.loc[~ sel].copy() # remove the transfers in (except for any return of excess)
  df=df.loc[~df.Description.str.contains('TRANSFER OF ASSETS')].copy() # remove transfer from devenir to fidelity
  df.Amount = - df.Amount # change sign
  # remove refunds to hsa
  sel = ~ df.Description.str.contains('ADJ') 
  df=df.loc[sel].copy()

  summary= df.pivot_table(index='Target Account',values='Amount',columns='Year',aggfunc='sum')
  summary=summary.reset_index()
  summary.rename(columns={'Target Account':'Account'},inplace=True)
  summary.Account=summary.Account.str.strip()
  return summary

def sel_inv_transfers(data_info):
  '''Get amounts transferred to/from certain brokerages, mutual funds, loans from/to any banks.
  
  The single input file is produced as a detailed transfer report in Moneydance
  It includes selected investment accounts, all banks.
  The input also includes investment income and expense categories, which are only used for accounts where 
  no reinvestment policy is in place (currently hardcoded)

  Assumptions:
    If passthru is used, it must only be used to transfer funds to/from banks

  arguments: 
    data_info a dict with the path to the file
  returns: dataframe with investment accounts for rows and years for columns
    positive values indicate amount moved out of bank into savings/investment
  '''
  filename=data_info['path']
  txt_flds=['Target Account',  'Source Account', 'Description', 'Memo']
  df=tsv_to_df(filename,skiprows=3,string_fields=txt_flds)
  df=df.loc[~pd.isnull(df[df.columns[:-1]]).all(axis=1)].copy() # blank rows (the reader replaces the null in the amount with zero)
  labels=pd.isnull(df[df.columns[1:][:-1]]).all(axis=1)
  stack=[]
  for ix,row in df.loc[labels].iterrows():
    ta=row['Target Account'].strip()
    if ta.startswith('TRANSFERS')| ta.startswith('TOTAL'):
      continue
    if ta.endswith('TOTAL'):
      stack.pop()   
    else:
      stack+=[ta]
      df.at[ix,'Target Account']=':'.join(stack)
  df['Target Account'].fillna(method='ffill',inplace=True)
  df=df.loc[~labels]    
  df=df.rename(columns={'Target Account':'Category','Source Account':'Account'})
  # remove the expense items in case they are provided
  df=df.loc[~df['Category'].str[:2].isin(['X:','T:'])]
  # and the income unless no reinvestment
  sel= df['Category'].str[:2].isin(['I:'])
  sel = sel  & ~ (df.Account=='LON - JNT - HED') # TODO generalize
  df=df.loc[~sel]
  df=setup_year(df)

  suma= df.pivot_table(index='Account',values='Amount',columns='Year',aggfunc='sum').reset_index()
  return suma

def five_29_distr(data_info):
  '''Get the 529 plan distribution records from Moneydance export and summarize so data items can be put in spreadsheet
  These data refer to 529 distributions

  Args: 
    data_info: dict that has a value for path used to locate the input file    
  
  Returns: 
    a dataframe with 529 accounts as rows and multiple y_year columns
    positives are amount distributed
    Only has columns where data exists
  '''
  filename=data_info['path']
  df=tsv_to_df(filename,skiprows=3,string_fields='Account,Category,Description,Tags,C'.split(','))
  sel=df.Account.str.startswith('CHET') | df.Account.str.startswith('529')
  df=df.loc[sel].copy()
  df.Amount=-df.Amount
  df=setup_year(df)
  summary=df.pivot_table(index='Account',values='Amount',columns='Year',aggfunc='sum')
  summary.fillna(value=0,inplace=True)
  summary=summary.reset_index()    
  return summary

def IRA_distr(data_info):
  '''Get the IRA distribution records from Moneydance export and summarize so data items can be put in spreadsheet
  These data refer to IRA distributions and the related tax withholding

  Args: 
    data_info: dict that has a value for path used to locate the input file    
  
  Returns: 
    a dataframe with categories or accounts as rows and multiple y_year columns
    Categories are 
      the income distribution category (as positive)
      the expense (withholding) categories (as negative)
    The only account is 'Bank Accounts'
    Bank accounts and withholding numbers are stated as negatives
    Only has columns where data exists

  Raises: ValueError if final-rmd and a normal distribution occur in same year.
          It logically could but the current setup does not support it.
  '''
  final_cat='Income:I:Retirement income:IRA:Final-RMD'
  norm_distr_cat='Income:J:Distributions:IRA:Normal-Distr'
  
  filename=data_info['path']
  df=tsv_to_df(filename,skiprows=3,string_fields='Account,Category,Description,Tags,C'.split(','))
  df.dropna(how='any',inplace=True) # total and blank rows
  df=setup_year(df)
  summary=df.pivot_table(index='Category',values='Amount',columns='Year',aggfunc='sum')
  summary.fillna(value=0,inplace=True)
  summary=summary.reset_index()
  summary=summary.loc[~summary.Category.str.startswith('IRA')]

  tax_sel=summary.Category.str.endswith('IRA WH') # flag the taxes paid
  wh=summary.loc[tax_sel].copy()
  wh['Category']='Expenses:'+wh['Category']

  # just the row with any final RMD as a Series
  final_sel=summary.Category.str.contains(':'.join(final_cat.split(':')[1:]))
  final_rmd=summary.drop(columns='Category').loc[final_sel].sum(axis=0) # The gross amount

  # Distributions that are sourced from an account in MD
  #  are in one of the rows that are not withholding or the final RMD category
  #  These should be accounts like bank accounts or brokerage accounts and the sign will be reversed 
  
  #  compute the total normal distribution by adding the taxes back in
  net_norm_distr=summary.drop(columns='Category').loc[~(final_sel | tax_sel) ].sum(axis=0).mul(-1) # The net as positive

  # Both is not supported.  If this ever happens you will need to re-work how the taxes are handled
  if not ((final_rmd != 0) != (net_norm_distr!=0)).all(): # Either or both
    raise ValueError('Final-RMD and Normal IRA distributions occur in same year.')

  gross_norm_distr=net_norm_distr-(net_norm_distr!=0)*+wh.drop(columns='Category').sum(axis=0)
  gross_norm_distr=pd.concat([pd.Series(data=[norm_distr_cat],index=['Category']),gross_norm_distr])

  final_rmd=pd.concat([pd.Series(data=[final_cat],index=['Category']),final_rmd])# 
  final_rmd=pd.DataFrame(final_rmd).T
  gross_norm_distr=pd.DataFrame(gross_norm_distr).T
  summary=pd.concat([final_rmd,gross_norm_distr,wh])
  summary.fillna(0,inplace=True)
  summary.reset_index(drop=True,inplace=True)
  return summary

def hsa_disbursements(data_info):
  '''Get the HSA disbursement records from Moneydance export and summarize so data items can be put in spreadsheet
  These data refer to medical payments made from HSA accounts.  
  Positive values indicate disbursements.  

  Args: 
    data_info: dict that has a value for path used to locate the input file  
  
  Returns: 
    a dataframe with HSA disbursements by year
    Only has columns where data exists
  ''' 
  filename=data_info['path']
  df=tsv_to_df(filename,skiprows=3,string_fields='Target Account,Source Account,Description,Memo'.split(','))
  df.dropna(how='all',inplace=True) # blank rows
  acct=df[['Target Account']].copy()
  acct.fillna(method= 'ffill',inplace=True)#propogate accounts
  df['Target Account']=acct
  df=df.loc[df.Date.notna()] # remove headings and totals
  df=setup_year(df)  # create the year field to allow for pivot

  sel = ~ df.Description.str.upper().str.contains('EXCESS') # remove return of excess records
  df=df.loc[sel]

  summary= df.pivot_table(index='Source Account',values='Amount',columns='Year',aggfunc='sum')
  summary=summary.reset_index()
  summary.rename(columns={'Source Account':'Account'},inplace=True)
  summary.Account=summary.Account.str.strip()
  summary=pd.concat([summary.Account,-summary.drop('Account',axis=1)],axis=1)
  return summary

def med_liab_pmts(data_info):
  '''Get how the medical liabilities were paid for by year
    Args: 
    data_info: dict that has a value for path used to locate the input file  
  
  Returns: 
    a dataframe with sources accounts for rows and years for columns
  '''
  filename=data_info['path']
  df=tsv_to_df(filename,skiprows=3,string_fields='Account,Check#,Description,Category,Tags,C'.split(','))
  df.drop(columns=['Check#','Tags','C'],inplace=True)
  df.dropna(how='any',inplace=True) # blank rows & total
  df=setup_year(df)  # create the year field to allow for pivot
  summary= df.pivot_table(index='Account',values='Amount',columns='Year',aggfunc='sum')
  summary.fillna(value=0,inplace=True)
  summary=summary.reset_index()
  pass

def setup_year(df):
  '''Convert the date field and create a year field, returning revised dataframe'''
  df=df.copy()
  df.loc[:,'Year']=df['Date'].dt.year.astype(int)
  df.loc[:,'Year'] = df['Year'].apply('Y{}'.format)
  return df

if __name__=='__main__':
  # payroll_savings(data_info={'path':'data/payroll_to_savings.tsv'}) 
  # IRA_distr(data_info={'path':'data/ira-distr.tsv'})
  hsa_disbursements(data_info={'path':'data/hsa-disbursements.tsv'})
  # sel_inv_transfers(data_info={'path':'data/trans_bkg.tsv'})
  # five_29_distr(data_info={ 'path':'data/529-distr.tsv' })
  # med_liab_pmts(data_info={'path':'data/med_liab_pmts.tsv'})