'''traffic controller for getting local data'''
import pandas as pd
from dance.accounts_load import read_accounts, prepare_account_tab
from dance.balances_load import read_balances, prepare_balances_folding
from dance.iande_actl_load import prepare_iande_actl, read_iande_actl,y_year
from dance.invest_actl_load import read_and_prepare_invest_actl
from dance.invest_iande_load import read_and_prepare_invest_iande,prepare_invest_iande_ratios
from dance.other_actls import (IRA_distr, hsa_disbursements, payroll_savings,
                               sel_inv_transfers, five_29_distr,roth_contributions,tagged_transactions)
from dance.transfers_actl_load import (prepare_transfers_actl,
                                       read_transfers_actl)
from dance.taxes_load import prepare_taxes
from dance.retire_load import prepare_retire, prepare_retire_medical                                     
from dance.util.logs import get_logger

logger=get_logger(__file__)

def read_data(data_info,years=None,ffy=None,target_file=None,table_map=None,title_row=1):
  '''Read data and prepare datafor various tabs and prepare it for insertion into the workbook.
  Uses the type value in data_info to determine what to do.

  args:
    data_info: a dictionary that contains data to control the reading and preparation
    years: Some types require additional info such as the years for the column.
    ffy: first forecast year as integer
    target_file: supports the case when there is a need to look at previously written worksheets
    table_map: a dict mapping tables to worksheets, if it has not already been stored in the target file.
    title_row: Optional. The row number in Excel for the title row (needed to compute subtotals). Default 2.

  returns: dataframe with columns specific to the type and groups (which may be None)

  raises: ValueError when things don't make sense.
    Such as in the case of balances if there is an account not found in the accounts worksheet
    '''
  groups=None
  match data_info['type']:
    case 'md_529_distr':
      df=five_29_distr(data_info=data_info)
    case 'md_acct':
      df= read_accounts(data_info)
      df= prepare_account_tab(data_info,df)
      pass
    case 'md_bal2':
      df=read_balances(data_info,target_file)
      df,groups=prepare_balances_folding(years,df,workbook=target_file)
    case 'md_iande_actl':
      df=read_iande_actl(data_info=data_info)
      df,groups=prepare_iande_actl(workbook=target_file,target_sheet=data_info['sheet'],df=df,title_row=title_row,table_map=table_map)
    case 'md_transfers_actl':
      df=read_transfers_actl(data_info=data_info,target_file=target_file,table_map=table_map)
      df,groups=prepare_transfers_actl(workbook=target_file,df=df,f_fcast=ffy)
    case 'md_invest_iande_values':
      df=read_and_prepare_invest_iande(workbook=target_file,data_info=data_info)
    case 'md_invest_iande_ratios':
      df=read_and_prepare_invest_iande(workbook=target_file,data_info=data_info)
      df=prepare_invest_iande_ratios(df)
    case 'md_invest_actl':
      df=read_and_prepare_invest_actl(workbook=target_file,data_info=data_info,table_map=table_map)
    case 'md_hsa_disb':
      df=hsa_disbursements(data_info=data_info)
    case 'md_ira_distr':
      df=IRA_distr(data_info=data_info)
    case 'md_pr_sav':
      df=payroll_savings(data_info=data_info)
    case 'md_sel_inv':
      df=sel_inv_transfers(data_info=data_info,workbook=target_file,table_map=table_map)
    case 'md_tag_sums':
      df=tagged_transactions(data_info=data_info)
    case 'json_index': # a json file organized like: {index -> {column -> value}}
      df=pd.read_json(data_info['path'],orient='index')
      logger.debug('Read {}'.format(data_info['path']))
    case 'json_records': # a json file organized like: [{column -> value}, … , {column -> value}]
      df=pd.read_json(data_info['path'],orient='records',convert_dates=['Start Date'])
      logger.debug('Read {}'.format(data_info['path']))
    case 'tax_template':
      df,groups=prepare_taxes(data_info=data_info,workbook=target_file)
    case 'md_roth':
      df=roth_contributions(data_info=data_info)
    case 'retire_template':
      df=prepare_retire(data_info=data_info)
    case 'retire_medical_template':
      df=prepare_retire_medical(data_info=data_info)    
    case _:
      assert False,'Undefined type'
  return df,groups

def read_gen_state(config):
  '''General state comes from the file but elements can be set by the control program,
  so this is called prior to setting up the general_state variable which is then modified.
  So this allows it to be treated as an "internal" source not a "local" source, and yet
  most parameters can be edited in the file.

  args:
    config: the dict that contains the location of file

  returns: the parameter table dictionary.
  '''
  table_info=config['sheets']['gen_tables']['tables']
  for table in table_info:
    if table['name']=='tbl_gen_state':
      path=table['data']['path']
  df=pd.read_json(path,orient='index')
  gen_state=df.to_dict(orient='index')
  return gen_state



if __name__=='__main__':
  pass
  # put testing stuff here
