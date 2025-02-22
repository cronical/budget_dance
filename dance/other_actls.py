#! /usr/bin/env python
'''Process the payroll to savings records from Moneydance export (report: 401, HSA, ESP payroll data)'''
import warnings
from os.path import exists

import pandas as pd

from dance.util.files import tsv_to_df
from dance.util.logs import get_logger
from dance.util.tables import df_for_table_name

warnings.simplefilter(action='ignore', category=FutureWarning)

logger=get_logger(__file__)


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
  df=add_yyear_col(df)  # create the year field to allow for pivot


  # remove the transfers in (except for any return of excess)
  df.Description.fillna('',inplace=True)
  sel= df.Amount < 0 
  txt='EXCESS'
  sel[df.Description.str.upper().str.contains(txt)]=True

  # remove return due to insufficient funds 
  txt='RETURNED ITEM, INSUFFICIENT'
  sel[df.Description.str.upper().str.contains(txt)]=False

  df=df.loc[ sel].copy() 

  # remove transfer from devenir to fidelity
  df=df.loc[~df.Description.str.contains('TRANSFER OF ASSETS')].copy() 
  df.Amount = - df.Amount # change sign
  # remove refunds to hsa
  sel = ~ df.Description.str.contains('ADJ') 
  df=df.loc[sel].copy()

  summary= df.pivot_table(index='Target Account',values='Amount',columns='Year',aggfunc='sum')
  summary=summary.reset_index()
  summary.rename(columns={'Target Account':'Account'},inplace=True)
  summary.Account=summary.Account.str.strip()
  return summary

def roth_contributions(data_info):
  '''Get the roth contributions'''
  filename=data_info['path']
  df=tsv_to_df(filename,skiprows=3,string_fields='Account,Check#,Description,Category,Tags,C'.split(','))
  df.drop(columns=['Check#','Tags','C'],inplace=True)
  df.dropna(how='any',inplace=True) # blank rows & total
  df=add_yyear_col(df)  # create the year field to allow for pivot
  summary= df.pivot_table(index='Category',values='Amount',columns='Year',aggfunc='sum')
  summary.fillna(value=0,inplace=True)
  sel=summary.index.str.startswith('401K')
  sel = sel | summary.index.str.startswith('IRA')
  summary=-summary.loc[sel]
  summary=summary.reset_index()
  summary.rename(columns={'Category':'Account'},inplace=True)
  return summary

def sel_inv_transfers(data_info,workbook=None,table_map=None):
  '''Get amounts transferred to/from certain brokerages, mutual funds, loans from/to any banks.
  
  The single input file is produced as a detailed transfer report in Moneydance
  It includes selected investment accounts, all banks.
  The input also includes investment income and expense categories, which are only used for accounts where 
  no reinvestment policy is in place (currently hardcoded)

  Assumptions:
    If passthru is used, it must only be used to transfer funds to/from banks

  arguments: 
    data_info a dict with the path to the file
    workbook: the name of the workbook where we will find the account information.
    table_map: the dict that points to the sheet for the accounts table.

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
    if ta.endswith("-Other"):
      logger.error(f"{filename} contains {ta}. Must not contain other. Fix in Moneydance.")
      raise ValueError("Cannot process as this breaks odd/even logic for totals")
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
  # but to do that we'll need the reinv rate from accounts
  accounts=df_for_table_name(table_name='tbl_accounts',workbook=workbook,data_only=True,table_map=table_map)
  no_reinv=accounts.loc[accounts['Reinv Rate']==0].index.to_list()
  sel= df['Category'].str[:2].isin(['I:'])
  sel = sel  & ~ (df.Account.isin(no_reinv)) 
  df=df.loc[~sel]
  df=add_yyear_col(df)

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
  df=add_yyear_col(df)
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
          It logically could but is not currently supported.
  '''
  distr_base_cat='Income:J:Distributions:IRA:'
  
  filename=data_info['path']
  df=tsv_to_df(filename,skiprows=3,string_fields='Account,Category,Description,Tags,C'.split(','))
  df.dropna(how='any',inplace=True) # total and blank rows
  df=add_yyear_col(df)

  # amounts taken from each IRA - this is gross, i.e. prior to taking out taxes
  by_ira=df.pivot_table(index='Account',values='Amount',columns='Year',aggfunc='sum')
  by_ira=by_ira.loc[by_ira.index.str.startswith('IRA')].mul(-1)
  by_ira.reset_index(inplace=True)
  by_ira['Category']=distr_base_cat+by_ira.Account.astype(str)
  by_ira=by_ira.drop(columns='Account')

  summary=df.pivot_table(index='Category',values='Amount',columns='Year',aggfunc='sum')
  summary.fillna(value=0,inplace=True)
  summary=summary.reset_index()
  summary=summary.loc[~summary.Category.str.startswith('IRA')]

  tax_sel=summary.Category.str.endswith('IRA WH') # flag the taxes paid
  wh=summary.loc[tax_sel].copy()
  wh['Category']='Expenses:'+wh['Category']

  summary=pd.concat([by_ira,wh])
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
  string_fields="Account,Date,Description,Category,Tags".split(",")
  df=tsv_to_df(filename,skiprows=3,string_fields=string_fields,usecols=string_fields+['Amount'])
  df.loc[df.Account=='Total']=None
  sel=df.Account.notna()
  df=df.loc[sel] # Total & blank rows

  year=df['Date'].dt.year
  year.name='Year'
  df=pd.concat([df,year],axis=1)

  sel = df.Tags=='hsa-distr'
  df=df.loc[sel]
  df.loc[df.index,'Amount']=-1*df.Amount

  df=df.fillna('')
  sel = ~ df.Description.str.upper().str.contains('EXCESS') # remove return of excess records
  df=df.loc[sel]

  summary= df.pivot_table(index='Account',values='Amount',columns='Year',aggfunc='sum')
  mapper=dict(zip(summary.columns,[f"Y{c}" for c in summary.columns]))
  summary.rename(columns=mapper,inplace=True)
  summary=summary.reset_index()

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
  df=add_yyear_col(df)  # create the year field to allow for pivot
  summary= df.pivot_table(index='Account',values='Amount',columns='Year',aggfunc='sum')
  summary.fillna(value=0,inplace=True)
  summary=summary.reset_index()
  pass

def tagged_transactions(data_info):
  ''' Process tagged records to create useful dataframe that summarizes by tags
  which were saved as tsv file. Modify MD report "Tagged Export" to add new tags.
  Starting with 'acct-move' but should be able to replace other tag logic.

  Raises error if more than one tag is used on a transaction.

  Returns dataframe with range index, a Tags column, an Account column and columns for the Y Years found in the input file
  '''

  filename=data_info['path']
  df=tsv_to_df(filename,skiprows=3,string_fields='Account,Check#,Description,Category,Tags,C'.split(','))
  df.drop(columns=['Check#','C'],inplace=True)
  df=df.loc[df.Category.notna()] # remove trailing blank row & total
  for ix,row in df.iterrows():
    # replace form tag, [tag] with just the first item (not sure why MD does this)
    tags=row['Tags'].split(', [')
    match len(tags):
      case 1:
        a=tags[0].replace('[','')
        a=a.replace(']','')
        df.at[ix,'Tags']=a
        continue
      case 2:
        a,b=tags
        b=b[:-1] # trailing bracket
        if b==a:
          df.at[ix,'Tags']=a
      case _:
        raise ValueError("Unexpect value in tags field")

  if df.Tags.str.contains(',').sum()>0:
    raise ValueError(f"The Tags field in file {filename} contains more than one tag on some records. Not supported.")
  df=add_yyear_col(df)  # create the year field to allow for pivot
  summary= df.pivot_table(index=['Tags','Account'],values='Amount',columns='Year',aggfunc='sum')
  summary.fillna(value=0,inplace=True)
  summary=summary.reset_index()

  # clean up by getting rid of zeros (eg from passthru amounts getting offset)
  sel=summary.drop(columns=['Tags','Account']).sum(axis=1)==0
  pt=summary.loc[sel].Account.str.startswith('Passthru')
  if pt.all():
    summary=summary.loc[~sel]
  else:
    bad=', '.join(summary.loc[sel].loc[~pt].to_list())
    raise ValueError(f"Zeros occurred in non-passthru account(s): {bad}.  Probably a mistake on a transaction.")
  summary.rename(columns={'Tags':'Tag'},inplace=True) # MD can have multiple, but we force to single
  return summary

def add_yyear_col(df):
  '''Convert the date field and create a year field, returning revised dataframe'''
  df=df.copy()
  df.loc[:,'Year']=df['Date'].dt.year.astype(int)
  df.loc[:,'Year'] = df['Year'].apply('Y{}'.format)
  return df

if __name__=='__main__':
  pass
  from dance.util.files import read_config
  config=read_config()
  workbook=config['workbook']
  #payroll_savings(data_info={'path':'data/payroll_to_savings.tsv'}) 
  roth_contributions(data_info={'path':'data/roth_contributions.tsv'})
  #IRA_distr(data_info={'path':'data/ira-distr.tsv'})
  # hsa_disbursements(data_info={'path':'data/tagged.tsv'})
  # sel_inv_transfers(workbook=workbook,data_info={'path':'data/trans_bkg.tsv'})
  # five_29_distr(data_info={ 'path':'data/529-distr.tsv' })
  # med_liab_pmts(data_info={'path':'data/med_liab_pmts.tsv'})
  #tagged_transactions(data_info={'path':'data/tagged.tsv'})
  