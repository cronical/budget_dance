'''Code for reading balances and preparing balances tab
'''
import pandas as pd
from openpyxl import load_workbook

from dance.accounts_load import read_accounts
from dance.util.files import read_config
from dance.util.row_tree import folding_groups,subtotal_formulas
from dance.util.logs import get_logger
from dance.util.tables import columns_for_table,conform_table

logger=get_logger(__file__)

def read_balances(data_info,target_file):
  bal_df=read_accounts(data_info)
  acct_df=pd.read_excel(target_file,sheet_name='accounts',skiprows=1)
  if len(bal_df)!=len(bal_df.merge(acct_df,on='Account')): # make sure all the balances are in the account list

    raise ValueError('Balance account(s) are not all in the Accounts table')
  logger.info('All balance accounts are in the accounts table.')
  bal_df=acct_df[['Account']].merge(bal_df[['Account','Current Balance']],on='Account',how='left').fillna(value=0)

  return bal_df

def prepare_balances_folding(years,in_df,workbook):
  '''Setup a folding version of the balances table to avoid dependencies in the same column.
  args:
    years: iterable with the numeric years to be appended to the columns
    in_df: a dataframe with at least the Account and Current Balance columns

  returns: a dataframe for the balance tab with the years columns set as None.

  The forecast and actuals items in the years columns are set later based on config.
  '''
 
  lead_cols=['Key','ValType','AcctName','Type','Income Txbl','Active','No Distr Plan']

  # the actual and the forecast formulas specified in setup.yaml - except for the opening balance

# wrap with account name and account name -  TOTAL
  suffixes=',:Start Bal,:Add/Wdraw,:Retain,:Retain:Rlz Int/Gn,:Retain:Reinv Rate,:Retain - PRODUCT,'
  suffixes+= ':Unrlzd,:Unrlzd:Actl Unrlz,:Unrlzd:Fcst,:Unrlzd:Fcst:I Start Bal,:Unrlzd:Fcst:Mkt Gn Rate,:Unrlzd:Fcst - PRODUCT,:Unrlzd - TOTAL,'
  suffixes+= ':Fees, - TOTAL'
  suffixes=suffixes.split(',')
  val_types={}
  for a in suffixes:
    val_types[a]=a.split(':')[-1]
  val_types[':Retain']='Hdg'
  val_types[':Unrlzd']='Hdg'
  val_types[':Unrlzd:Fcst']='Hdg'
  val_types[':Unrlzd:Fcst - PRODUCT']='Fcst Unrlz'
  val_types[":Unrlzd - TOTAL"]="Unrlz Gn/Ls"
  val_types[":Retain - PRODUCT"]="Reinv Amt"
  val_types[" - TOTAL"]="End Bal"

  r_count=len(suffixes)
  df=pd.DataFrame([]) # accumulate into this
  # prepare the data for each account 
  for _,row in in_df.iterrows():
    acct=row['Account']
    acct_df=pd.DataFrame([])
    acct_df['Key']=[acct+a for a in suffixes]
    for c in lead_cols:
      if c== 'ValType':
        acct_df[c]=val_types.values()
      if c== 'AcctName':
        acct_df[c]=[row['Account']]*r_count

    formulas=[None]*r_count
    for c in years:
      yx=years.index(c)
      if yx==0:
        for ix,vt in enumerate(val_types.values()):
          if vt == 'Start Bal': # start bal for 1st year - used to calculate end balance
            formulas[ix]="=%.2f"% in_df.loc[in_df.Account == row['Account'],'Current Balance']

      acct_df['Y{}'.format(c)]=formulas
    df=pd.concat([df,acct_df],axis=0)
  df.reset_index(inplace=True,drop=True)  
  df['level']=df.Key.str.count(':')
  df['is_leaf']=~(df.Key.str.endswith('TOTAL') | (df.Key.str.endswith('PRODUCT')))

  assert 8>=df.level.max(), 'Highest level is %d.  Excel max is 8'%df.level.max()
  df,groups=folding_groups(df)
  wb = load_workbook(filename = workbook, read_only=False, keep_vba=True)
  col_def=columns_for_table(wb,'balances','tbl_balances',read_config())
  df=conform_table(df,col_def['name'])  
  df=subtotal_formulas(df,groups)
  return df,groups

