#! /usr/bin/env python
'''
Reads data from "data/taxes_template.tsv" to create the taxes table
'''
import argparse

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from dance.util.files import tsv_to_df,read_config
from dance.util.tables import agg_types,columns_for_table,conform_table

def nest(df,source_field):
  '''Create key of nested category names
  determine level of each row in the category hierarchy
  
  returns a new dataframe with a field, Key, in the first column
  
  '''

  # hold the flat view in the key column for now
  df.insert(loc=0,column='Key',value=df[source_field].str.lstrip()) # used to define level
  #create a level indicator, re-use the totals column which for 'level', to be removed later before inserting into wb
  df['level']=((df[source_field].str.len() - df.Key.str.len()))/3 # each level is indented 3 more spaces
  df['level']=[int(x) for x in df.level.tolist()]
  df['Key']=None # build up the keys by including parents
  last_level=-1
  pathparts=[]
  pathpart=None
  for ix,row in df[['level',source_field]].iterrows():
    lev=row['level']
    if lev > last_level and pathpart is not None:
      pathparts.append(pathpart)
    if lev < last_level:
      pathparts=pathparts[:-1]
    pathpart=row[source_field].strip()
    a=pathparts.copy()
    a.append(pathpart)
    key=':'.join(a)
    df.loc[ix,'Key']=key
    last_level=lev
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

def subtotal_formulas(df,groups):
  '''Replace the hard values with formulas
  if its not a total just let the value stay there'''
  for group in groups:
    key=df.at[group[2]-2,'Key']
    agg=key.split(' - ')[-1]
    code=agg_types[agg]
    for cx,cl in enumerate(df.columns):
      if cl.startswith('Y'):
        let=get_column_letter(cx+1)
        formula='=subtotal({},{}{}:{}{})'.format(code,let,group[1],let,group[2])
        df.loc[group[2]-2,[cl]]=formula
  return df

def prepare_taxes(data_info,workbook):
  '''setup the taxes dataframe'''
  string_fields='Line,Agg_method,Tax_doc_ref,Notes,Source,Tab'.split(',')
  df=tsv_to_df(data_info['path'],skiprows=3,nan_is_zero=False,string_fields=string_fields)

  # remove Y columns (they are there just to test the subtotaling at the template level)
  cols=df.columns.to_list()
  remove_cols=[c for c in cols if (c[0]=='Y') & c[1:].isnumeric()]
  df.drop(columns=remove_cols,inplace=True)

  df=nest(df,'Line')
  df,groups=folding_groups(df)
  wb = load_workbook(filename = workbook, read_only=False, keep_vba=True)
  col_def=columns_for_table(wb,'taxes','tbl_taxes',read_config())
  df=conform_table(df,col_def['name'])  
  df=subtotal_formulas(df,groups)
  return df,groups

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description ='Prepares the taxes table from the input template')
  parser.add_argument('--workbook','-w',default='data/test_wb.xlsm',help='Target workbook')# TODO fcast
  parser.add_argument('--path','-p',default= 'data/taxes_template.tsv',help='The path and name of the input file')
  args=parser.parse_args()
  prepare_taxes(data_info={'path':args.path},workbook=args.workbook)