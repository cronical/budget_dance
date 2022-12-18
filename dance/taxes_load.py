#! /usr/bin/env python
'''
Reads data from "data/taxes_template.tsv" to create the taxes table
'''
import argparse
from dance.util.files import tsv_to_df

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
  return df.drop('level',axis=1)

def prepare_taxes(workbook,path):
  '''setup the taxes dataframe'''
  string_fields='line,agg_method,tax_doc_ref,notes,source,actl_source_tab,fcast_source_tab'.split(',')
  df=tsv_to_df(path,skiprows=3,nan_is_zero=False,string_fields=string_fields)
  df=nest(df,'line')
  pass

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description ='Prepares the taxes table from the input template')
  parser.add_argument('--workbook','-w',default='data/test_wb.xlsm',help='Target workbook')# TODO fcast
  parser.add_argument('--path','-p',default= 'data/taxes_template.tsv',help='The path and name of the input file')
  args=parser.parse_args()
  prepare_taxes(workbook=args.workbook,path=args.path)