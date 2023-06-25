'''Functions to support row hierarchy.'''

from openpyxl.utils import get_column_letter

import pandas as pd


def hier_insert(df,table_info,sep=":"):
  '''Insert any specified new rows
  args:
    df - a dataframe with the Key in a column
    table_info - a dict which may have key "hier_insert_paths"

  returns: the possibly modified dataframe
  '''
  if not 'hier_insert_paths' in table_info['data']:
    return df
  for path in table_info['data']['hier_insert_paths']:
    if path in df['Key'].tolist():
      continue
    # determine which subpaths need to be inserted
    to_insert=[] # headings and the row itself
    path_parts=path.split(sep)
    for ix,_ in enumerate(path_parts):
      subpath=sep.join(path_parts[0:ix+1])
      if subpath in df['Key'].tolist():
        continue
      to_insert+=[subpath]
    totals=to_insert.copy()[:-1]
    totals.reverse()
    totals=[t + ' - TOTAL' for t in totals]
    to_insert+= totals
    cols=df.columns
    insert_df=pd.DataFrame({cols[0]:to_insert,
      cols[1]:[indent_leaf(p) for p in to_insert],
      'level': [s.count(':') for s in to_insert]})
    new_df=pd.concat([df,insert_df]).fillna(0)
    # sort so they are in the right order by sorting on the list of the path path parts
    sort_key=new_df['Key'].to_list()
    sort_key=[s.replace('Income','Alpha') for s in sort_key] # sort income before expenses
    new_df['sortable']=[k.split(':') for k in sort_key]
    new_df.sort_values('sortable',inplace=True)
    new_df.reset_index(drop=True,inplace=True)
    del new_df['sortable']
    df=new_df.copy()
  return df

def identify_groups(df):
  '''identify groups where folding and subtotals occur
  Whenever the level goes down from the previous level it may be a total.
  Typically it is a total, but in the case of a deeper level in the middle of a tranche of a certain level
  it may not be.

  returns list of triples of group info: level, start, end
  '''
  groups=[] 
  last_level=-1
  keys=list(df['Key'])
  for ix,row in df.iterrows():
    level_change= row['level']-last_level
    k=row['Key']# get the key value from the file
    if level_change <0: #this might be a total line
      n=k.find(' - TOTAL') # see if it has the total label
      if n >= 0: # if it has a total label
        bare = k[:n]# # remove the total label
        try:
          # prepare the grouping specs
          bx=keys.index(bare) # look for this in the keys - should be there
          groups.append([row['level']+1,bx+3,ix+2]) # 3 accounts for 1 to change origin, 1 header row, 1 title row
        except ValueError as e:
          raise ValueError(f'{k} not found in keys'.format()) from e
    last_level=row['level']
  return groups

def indent_leaf(path,sep=':',spaces=3):
  '''Convert a path with separators to show level of the leaf by using spaces
  args:
    path - a string with separators
    sep - the separator to use
    spaces - the number of spaces for each level

  returns: string with the leaf from the path preceded by spaces to show the level.
  '''
  n=path.count(sep)*spaces
  result=(' '*n)+path.split(':')[-1]
  return result

def is_leaf(df):
  '''add a field, is_leaf, to a dataframe by marking leaf nodes with 1, other wise 0'''
  df.insert(loc=1,column='is_leaf',value=0) 
  sel= df.level >= df.level.shift(periods=-1,fill_value=0)
  sel = sel & ~ df.Key.str.endswith('TOTAL')
  df.loc[sel,'is_leaf']=1
  return df

def nest_by_cat(df,cat_field='Account',spaces_per_level=3):
  '''create key of nested "category" names based on the field named in cat_field
   determines level of each row in the category hierarchy
   and whether the row is a leaf node
   returns df with key, is_leaf and level columns'''
  if not 'Key' in df.columns:
    df.insert(loc=0,column='Key',value=None)
  df['Key']=df[cat_field].str.lstrip() # used to define level
  #create a level indicator, re-use the totals column which for 'level', to be removed later before inserting into wb
  df['level']=((df[cat_field].str.len() - df.Key.str.len()))/spaces_per_level # each level is indented 3 more spaces
  df['level']=[int(x) for x in df.level.tolist()]

  df['Key']=None # build up the keys by including parents
  last_level=-1
  pathparts=[]
  pathpart=None
  for ix,row in df[['level',cat_field]].iterrows():
    lev=row['level']
    if lev > last_level and pathpart is not None:
      pathparts.append(pathpart)
    if lev < last_level:
      pathparts=pathparts[:-1]
    pathpart=row[cat_field].strip()
    a=pathparts.copy()
    a.append(pathpart)
    key=':'.join(a)
    df.loc[ix,'Key']=key
    last_level=lev
  return df


def subtotal_formulas(df,groups,heading_row):  
  '''On subtotal rows replace the existing (hard) values with formulas
  if its not a total just let the value stay there
  '''
  for group in groups:
    for cx,cl in enumerate(df.columns):
      if str(cl).startswith('Y'):
        let=get_column_letter(cx+1)
        formula='=subtotal(9,{}{}:{}{})'.format(let,group[1],let,group[2])
        df.loc[group[2]-2,[cl]]=formula

  keys=df.Key.tolist()
  grand_total='TOTAL INCOME - EXPENSES' # support for iande etc.
  if grand_total in keys:
    net_ix=keys.index(grand_total) # find the net line (its should be the last line)
    group=groups[-1]
    inc_ix=keys.index('Income - TOTAL')+heading_row+1 # offset for excel
    exp_ix=keys.index('Expenses - TOTAL')+heading_row+1
    for cx,cl in enumerate(df.columns):
      if str(cl).startswith('Y'):
        let=get_column_letter(cx+1)
        formula='={}{}-{}{}'.format(let,inc_ix,let,exp_ix)
        df.loc[net_ix,[cl]]=formula
  return df