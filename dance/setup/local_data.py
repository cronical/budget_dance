'''get annual various local data'''
import pandas as pd
from dance.util.files import tsv_to_df

def read_data(data_info):
  if data_info['type']== 'md_acct':
    df= read_accounts(data_info)
    df= prepare_account_tab(data_info,df)
    return df

def filter_nz(df,include_zeros):
  '''get a filter for the the rows in a dataframe that have a balance or are allowed by config.

  args:
    df: a dataframe with fields, Current Balance and Account
    include_zeros: a list of account names that should be kept even if zero

  returns: boolean series, where True indicates item should be kept.
  '''
  nz=df['Current Balance']!=0
  za=df['Account'].apply(lambda x: x in include_zeros)
  nzza=pd.concat([nz, za],axis=1)
  return nzza.any(axis=1)

# -----------------------------
def read_accounts(data_info):
  '''Get the account data as specified in the data_info.

  Depending on the data_info may take items at a total level or leaf level.

  args:
    data_info: a dictionary with the path of the source file, and three lists:
    1. group - identifies categories or total levels (with subaccounts)
    2. no_details_for - identifies categories that are covered by total levels
    3. include_zeros - indicates accounts that are wanted even though they are zero balance (otherwise ignored)

  returns: dataframe including 'Account', 'Type', 'Current Balance' and 'total_type'
  '''
  # doing the same with data frame
  types={'Assets':'A','Bank Accounts':'B','Credit Cards':'C','Investment Accounts':'I','Liabilities':'L','Loans':'N'}
  groups=data_info['group']
  no_details_for=data_info['no_details_for']
  include_zeros=set(data_info['include_zeros'])
  include_zeros.update(groups)# add groups to the include zeros list
  g_totals=[g+' - Total' for g in groups]

  df=tsv_to_df(data_info['path'],skiprows=3)
  df=df.dropna(how='any',subset='Account')

  # establish category for each row
  df['category']=''
  cat='Bank Accounts'# should be in the first row, but this keeps it clean
  for ix,row in df.iterrows():
    if pd.isnull(row['Notes']):
      cat=row['Account']
      df.loc[ix,'Notes']='' # to allow selecting securities later
    df.loc[ix,'category']=cat

  #df=df.loc[~ df['Notes'].str.contains('@')] # remove securities / currencies (?)

  # build a boolean grid to track where each account is handled
  df.reset_index(drop=True,inplace=True)
  for col in ['ignore','by_total','keep']:
    df[col]=False

  # distinguish between category and sub-account totals to handle name conflicts
  df['total_type']='leaf'
  tot_rows=df['Account'].str.contains(' - Total')
  i_tots=pd.concat([tot_rows,df['category']=='Investment Accounts'],axis=1).all(axis=1)
  i_totals=list(set(df.loc[i_tots,'Account'])-{'Investment Accounts - Total'})
  for ix,row in df.loc[tot_rows,['Account']].iterrows():
    acct_total_key=row['Account']
    acct_key=' - '.join(acct_total_key.split(' - ')[:-1])
    # mark the heading and the total lines
    sel=df['Account'].apply(lambda x: x in [acct_key , acct_total_key])
    if sum(sel)==2: # the normal case
      df.loc[sel,'total_type']=['sub_account','category'][acct_key in types]
    if sum(sel)==4: # name conflict between category and sub-account total
      ixs= df.loc[sel].index.tolist()
      for y in ixs:
        df.loc[y,'total_type']=['sub_account','category'][y in [ixs[0],ixs[-1]]]
      sel=pd.concat([sel,df['total_type']=='sub_account'],axis=1).all(axis=1) # only include the sub_account variant
      assert sum(sel)==2, 'too many name conflicts on {}'.format(acct_key)

    # now that there is no name conflict, mark rows
    start,end=tuple(df.loc[sel,[]].index)
    df.loc[[start],'ignore']=True # no further use for headings
    ixs=range(start+1,end)
    if acct_total_key in g_totals+i_totals:
      df.loc[ixs,'keep']=False # leaf nodes covered by a total
      df.loc[end,'Account']=acct_key
      df.loc[[end],'keep']=filter_nz(df.loc[[end]],include_zeros)
      pass
    else:
      if acct_key not in no_details_for:
        sel2=filter_nz(df.loc[ixs],include_zeros)
        df.loc[ixs,'keep']=sel2# the leaf nodes we will keep unless we have a total at a higher level, in which case, they will later be overwritten
        df.loc[end+1,'keep']=False # totals we are ignoring

  df=df.loc[df.keep]
  df['Type']=[types[x] for x in df.category.tolist()]
  return df[['Account','Type','Current Balance','total_type']]

def prepare_account_tab(data_info, in_df):
  '''Add in the added fields
  args:
    data_info: a dictionary describing the data (from the config.yaml file)
    in_df: a dataframe with columns: Account, Type, Current Balance, and total_type

  returns: a dataframe for the accounts tab
  '''
  df=in_df
  tax_free_keys=[]
  if 'tax_free_keys'in data_info:
    tax_free_keys=data_info['tax_free_keys']
  account_names=df.Account.tolist()
  df['Income Txbl']= [ int(not any(y in x for y in tax_free_keys)) for x in account_names]
  df['Active']=(df[['Current Balance']] != 0).astype(int) # default zero accounts to inactive
  df['Rlz share']=0
  df['Unrlz share']=1
  source_formulas=[ '=@[Account]','=@[Account] & " - TOTAL"' ]  #formula for (sub-accounts),  (leaves, and categories)
  flag=pd.concat([df.total_type=='sub_account',df.Type!='I'],axis=1).all(axis=1)
  df['Actl_source']=[source_formulas[ x] for x in flag]
  source_tabs=['tbl_tranfers_actl','tbl_invest_actl']# actuals are sourced from this, (depends on account type)
  df['Actl_source_tab']= [source_tabs[x=='I']for x in df.Type.tolist()]
  df['Fcst_source']='zero' # a default, but should be changed by user
  del df['total_type']
  return df
