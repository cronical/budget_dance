'''Code for reading balances and preparing balances tab
'''

import pandas as pd

from dance.accounts_load import read_accounts
from dance.util.logs import get_logger
from dance.util.xl_formulas import this_row

logger=get_logger(__file__)

def read_balances(data_info,target_file):
  bal_df=read_accounts(data_info)
  acct_df=pd.read_excel(target_file,sheet_name='accounts',skiprows=1)
  if len(bal_df)!=len(bal_df.merge(acct_df,on='Account')): # make sure all the balances are in the account list

    raise ValueError('Balance account(s) are not all in the Accounts table')
  logger.info('All balance accounts are in the accounts table.')
  bal_df=acct_df[['Account']].merge(bal_df[['Account','Current Balance']],on='Account',how='left').fillna(value=0)

  return bal_df

def prepare_balance_tab(years,in_df):
  '''Add in the added fields for the balance worksheet
  args:
    years: iterable with the numeric years to be appended to the columns
    in_df: a dataframe with at least the Account and Current Balance columns

  returns: a dataframe for the balance tab with the years columns set as None.

  The forecast and actuals items in the years columns are set later based on config.
  '''

  acct_ref=this_row('AcctName')
  # TODO move repeated formulas to setup.yaml
  repeated_formulas={
    'Type':'=@get_val({},"tbl_accounts",D$2)'.format(acct_ref),
    'Income Txbl': '=@get_val( {},"tbl_accounts",E$2)'.format(acct_ref),
    'Active': '=@get_val( {},"tbl_accounts",F$2)'.format(acct_ref),
    'No Distr Plan': '=@get_val( {},"tbl_accounts",G$2)'.format(acct_ref)
  }
  #Now implemented below to make field static:    'Key':'=@CONCATENATE( {},{})'.format(this_row('ValType'), acct_ref),

  lead_cols=['Key','ValType','AcctName','Type','Income Txbl','Active','No Distr Plan','Reinv Rate']

  # the actual and the forecast formulas specified in setup.yaml - except for the opening balance

  val_types=['Mkt Gn Rate','Reinv Rate','Start Bal','Add/Wdraw','Rlz Int/Gn','Reinv Amt','Fees','Unrlz Gn/Ls','End Bal']
  r_count=len(val_types)
  df=pd.DataFrame([]) # accumulate into this
  
  # prepare the data for each account 
  for _,row in in_df.iterrows():
    acct_df=pd.DataFrame([])
    for c in lead_cols:
      if c in repeated_formulas:
        acct_df[c]=[repeated_formulas[c]]*r_count
      else:
        if c== 'ValType':
          acct_df[c]=val_types
        else:
          acct_df[c]=[row['Account']]*r_count
    for c in years:
      formulas=[]
      for vt in val_types:
        yx=years.index(c)
        formula=None
        if vt == 'Start Bal': # start bal for 1st year has to be carried in here.
          if yx == 0:
            formula=float(in_df.loc[in_df.Account == row['Account'],'Current Balance'])
        formulas+=[formula]
      acct_df['Y{}'.format(c)]=formulas
    df=pd.concat([df,acct_df],axis=0)
  df['Key']=df['ValType']+df['AcctName']  
  df.reset_index(inplace=True,drop=True)
  return df
