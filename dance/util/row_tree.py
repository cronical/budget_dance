'''Functions to support row hierarchy.'''

from openpyxl.utils import get_column_letter

import pandas as pd

agg_types={'MAX':4,'MIN':5,'PRODUCT':6,'TOTAL':9} # original excel native types
agg_types['FED_TAX']=-1
agg_types['CT_TAX']=-2

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
    for ix,tot in enumerate(totals):
      agg='TOTAL'
      if 'hier_alt_agg' in table_info['data']:
        hier_alt_agg=table_info['data']['hier_alt_agg']
        if tot in hier_alt_agg:
          agg=hier_alt_agg[tot]
      totals[ix]=tot + ' - ' + agg          
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

def folding_groups(df):
  '''prepare the groups for folding and remove the level field
  The subtotals are aligned with the groups
  Whenever the level goes down from the previous level it may be a total
  Separate function allows use if heirarchical insert if needed.
  
  returns modifed df and groups
  '''
  groups=[] # level, start, end
  last_level=-1
  keys=list(df['Key'])
  for ix,row in df.iterrows():
    level_change= row['level']-last_level
    k=row['Key']# get the key value from the file
    if level_change <0: #this might be a total line
      parts=k.split(' - ')# see if it has the total label
      # typically it is a total, but in the case of a deeper level in the middle of a tranche of a certain level
      # it may not be.
      if len(parts)>1:# if it has a total label
        agg=parts[-1]
        if not agg in agg_types:
          raise ValueError('Agg method not known: %s'%agg)
        bare = ' - '.join(parts[:-1]) # remove the total label
        try:
          # prepare the grouping specs
          bx=keys.index(bare) # look for this in the keys - should be there
          groups.append([row['level']+1,bx+3,ix+2]) # 3 accounts for 1 to change origin, 1 header row, 1 title row
        except ValueError as e:
          raise ValueError(f'{k} not found in keys'.format()) from e
    last_level=row['level']
  del df['level'] # clear out temp field  
  return df,groups

def multi_agg_subtotals(groups):
  '''for a each group determine what rows should be aggregated
  groups is a result of folding_groups and group is one of its members
  for type 9 (sum) this is not needed, but other types cannot have their constituents in the result
  for example row 7 is the min of rows 5 and 6 and 7 is further aggregated with 8 as a sum into 9
  in this case the result for the group with end of sums up 7 and 8 but not 5 and 6
  returns a list of row numbers to be summed for each group'''

  group_rows=[]
  groups_df=pd.DataFrame(groups,columns='level,start,end'.split(','))
  for group in groups:
    rows=set(range(group[1]+1,group[2]+1)) # all possible rows
  # add one to start of group to not include the heading line which is blank.
  # blank works ok for sum but not for min, max, product  
    sel=(groups_df.start > group[1]) & (groups_df.end<group[2]) & (groups_df.level==1+group[0])
    for _,row in groups_df.loc[sel].iterrows():
      rows=rows - set(range(row[1],row[2]+1))
    rows=list(rows)
    group_rows+=[sorted(rows)]
  return group_rows


def collapse_adjacent(seq):
  '''given a list of non-negative integers in ascending order, detect spans where the gap between successive elements is 1
  replace those spans with a two element tuple that includes the start and end'''
  r=[]
  candidate=[-1,-1]
  def post(r,candidate):
    if candidate[0]==-1:
      return r
    if candidate[1]==-1:
      r.append(candidate[0])
    else:
      r.append(tuple(candidate))
    return r
  for n in seq:
    if candidate[0]>0:
      if (n-max(candidate))==1:
        candidate[1]=n
      else:
        r=post(r,candidate)
        candidate=[n,-1]
    else:
      candidate[0]=n
  r=post(r,candidate)
  return r

def address_phrase(let,collapsed_seq):
  '''given a list consisting of integers and/or two element tuples of integers produce Excel addresses.
  let is the column letter
  collapsed_seq is result of collapse_adjacent
  Returns string with commas separating ranges/addresses'''
  a=[]
  for item in collapsed_seq:
    if isinstance(item,tuple):
      f='%s%d:%s%d'%(let,item[0],let,item[1])
    else:
      f='%s%d'%(let,item)
    a.append(f)
  r=','.join(a)
  return r

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
  df['level']=df.level.astype(int)
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

def subtotal_formulas(df,groups):
  '''Replace the aggregate lines values with formulas
  if its not an aggregate just let the value stay there
  Supports aggregation by TOTAL, MIN, MAX, PRODUCT, FED_TAX

  Works by enumerating the ranges to aggregate.  
  Unlike the subtotal method this grabs the subordinate aggregation lines not the underlying leaf nodes
  This methods allows the folding to do things like sum the results of subordinate aggregations that are not themselves sums.

  Returns revised dataframe
  '''

  agg_rows=multi_agg_subtotals(groups)
  for gx,group in enumerate(groups):
    key=df.at[group[2]-2,'Key']
    agg=key.split(' - ')[-1]
    code=agg_types[agg] 
    func={4:"MAX",5:"MIN",6:"PRODUCT",9:"SUM",-1:"TX_FED",-2:"TX_CT"}[code]
    for cx,cl in enumerate(df.columns):
      if cl.startswith('Y'):
        let=get_column_letter(cx+1)
        addrs=address_phrase(let,collapse_adjacent(agg_rows[gx]))
        if code >0:
          formula='={}({})'.format(func,addrs)
          if code==9: # try to keep out decimals from messing up zero formatting.
            formula='=ROUND({},2)'.format(formula[1:])
        if code <0:
          tbl="tbl_{}_tax".format(func.split('_')[1].lower())
          formula='={}({}[],{})'.format(func,tbl,addrs)
        # retain following line - to allow switch back to subtotal method
        #formula='=subtotal({},{}{}:{}{})'.format(code,let,group[1]+1,let,group[2])
        df.loc[group[2]-2,[cl]]=formula
  return df

