#! /usr/bin/env python
'''
Copies data from "data/iande.tsv" into tab "iande_actl" after doing some checks.
'''
import argparse
import datetime

import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from dance.util.books import col_attrs_for_sheet, fresh_sheet, set_col_attrs
from dance.util.files import read_config, tsv_to_df
from dance.util.logs import get_logger
from dance.util.tables import (columns_for_table, df_for_table_name,
                               get_f_fcast_year, this_row, write_table)
from dance.util.xl_formulas import actual_formulas, forecast_formulas, table_ref

logger=get_logger(__file__)

def test_required_lines(df,workbook,forecast_start_year,initialize_iande=False,force=False,verbose=False):
  ''' Test the proposed updates to income and expense, to keep iande and iande_actl aligned.
  Compute the list of required lines given the forecast start year in form y_year
  Args:
    df: the dataframe containing the proposed replacement for iande_actl
    workbook: the name of the target excel file
    forecast_start_year: The first forecast year as a String (Ynnnn)
    initialize_iande: True if we are going to (re)initialize iande. Default False.
    force: True if we are going to allow forecast values to be destroyed. Default False
    verbose: True to report out all the lines that are in actl but not in iande. default False.

  returns: the required lines and all lines as sets

  raises:
    ValueError: when removing non-zero forecast lines without the -f (force) flag

  '''
  logger.debug('Testing required lines')
  try:
    iande=df_for_table_name(table_name='tbl_iande',workbook=workbook)
  except ValueError as err:
    logger.warning(str(err))
    logger.warning('Unable to check required lines')
    return
  iande.insert(loc=0,column='Key',value=iande.index) # it comes with the key as the index
  iande.reset_index(drop=True,inplace=True)
  cols= list(iande.columns)
  ix=cols.index(forecast_start_year)
  c=cols[ix:]

  def not_all_are_empty(a):
    return any([x is not None for x in list(a)])

  req_lines=set(iande.Key.loc[iande[c].apply(not_all_are_empty,axis=1)])
  # make sure nothing of the forecast gets lost due to changed lines.

  keys=list(df['Key'])
  if not req_lines.issubset(set(keys)):
    logger.warning('Existing forecast lines are not all present')
    logger.warning('The following line(s) exist in {} but do not occur in the file to import ({})'\
      .format(workbook,workbook))
    missing=list(req_lines.difference(set(keys)))
    for ms in missing:
      logger.info('   {}'.format(ms))
    logger.info('Intialize iande flag is set to %r',initialize_iande)
    if initialize_iande:
      print('That will remove those forecast lines from iande')
      if not force:
        logger.error('Exiting {}. Re-run with -f to continue'.format(__file__))
        raise ValueError('Proposed removing forecast lines without the -f (force) flag')
    else:
      logger.info('But we are only updating iande_actl, it does not matter.')
  else:
    logger.debug('All forecast items are included in input file.')

  # now report any new lines
  all_lines=set(iande.index)
  new=list(set(keys).difference(all_lines))
  new.sort()
  if 0<len(new):
    logger.info('Note: new lines will be in iande_actl but not in iande')
    logger.info('These may be added later by the program and/or you can manually add them there')
    logger.info('Note: lines with the suffix "-Other" occur when a transaction exists at a non-leaf in the category tree')
    logger.info('      If not desired, remove transaction and run again.  ')
    if verbose:
      for nw in new:
        logger.info('   {}'.format(nw))
    else:
      logger.info('To see the list re-run with verbose option')

def indent_other(str):
  '''indent -other rows to fix an anomoly in the md report
  '''
  if -1==str.find('-Other'):
    return str
  else:
    return '   '+str

def read_iande_actl(data_info):
  '''  Read data from file into a dataframe

  args:
    data_info: dict that has a value for path used to locate the input file

  returns: dataframe with index as 0...n

  raises:
    FileNotFoundError: if the input file does not exist.
  '''
  input_file=data_info['path']

  # get the input data from file
  try:
    df=tsv_to_df (input_file,skiprows=3)
    logger.info('loaded dataframe from {}'.format(input_file))
  except FileNotFoundError as e:
    raise f'file not found {input_file}' from e

  # some data clean ups
  df.fillna(0, inplace=True) # replace the NaN's with zeros
  df.query('Account!=0',inplace=True) # remove blank rows
  df.Account=df.Account.apply(indent_other)
  if 'Total' in df.columns:
    del df['Total']
  df.reset_index(drop=True,inplace=True)
  return df

def y_year(df):
  '''change the year columns to Y+year format'''
  for cn in df.columns.values.tolist():
    if cn.isnumeric():
      n=int(cn)
      nn = 'Y{}'.format(n)
      df.rename(columns={cn:nn},inplace=True) 
  return df 

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

def nest_by_cat(df):
  '''create key of nested category names
   determines level of each row in the category hierarchy
   and whether the row is a leaf node
   returns df with key, is_leaf and level columns'''
  df.insert(loc=0,column='Key',value=df.Account.str.lstrip()) # used to define level
  #create a level indicator, re-use the totals column which for 'level', to be removed later before inserting into wb
  df['level']=((df.Account.str.len() - df.Key.str.len()))/3 # each level is indented 3 more spaces
  df['level']=[int(x) for x in df.level.tolist()]

  df['Key']=None # build up the keys by including parents
  last_level=-1
  pathparts=[]
  pathpart=None
  for ix,row in df[['level','Account']].iterrows():
    lev=row['level']
    if lev > last_level and pathpart is not None:
      pathparts.append(pathpart)
    if lev < last_level:
      pathparts=pathparts[:-1]
    pathpart=row['Account'].strip()
    a=pathparts.copy()
    a.append(pathpart)
    key=':'.join(a)
    df.loc[ix,'Key']=key
    last_level=lev
  return df

def is_leaf(df):
  '''add a field, is_leaf, to a dataframe by marking leaf nodes with 1, other wise 0'''
  df.insert(loc=1,column='is_leaf',value=0) 
  sel= df.level >= df.level.shift(periods=-1,fill_value=0)
  sel = sel & ~ df.Key.str.endswith('TOTAL')
  df.loc[sel,'is_leaf']=1
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

def hier_insert(df,table_info):
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
    path_parts=path.split(':')
    for ix,_ in enumerate(path_parts):
      subpath=':'.join(path_parts[0:ix+1])
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
  net_ix=keys.index('TOTAL INCOME - EXPENSES') # find the net line (its should be the last line)
  if -1!=net_ix:
    group=groups[-1]
    inc_ix=keys.index('Income - TOTAL')+heading_row+1 # offset for excel
    exp_ix=keys.index('Expenses - TOTAL')+heading_row+1
    for cx,cl in enumerate(df.columns):
      if str(cl).startswith('Y'):
        let=get_column_letter(cx+1)
        formula='={}{}-{}{}'.format(let,inc_ix,let,exp_ix)
        df.loc[net_ix,[cl]]=formula
  return df

def prepare_iande_actl(workbook,target_sheet,df,force=False,f_fcast=None,title_row=1,verbose=False):
  '''prepare the dataframe for insertion into workbook. Supports both iande and iande_actl.
    Makes checks to ensure nothing of the forecast gets lost due to changed lines.
    Checks can be overridden by a flag.
    Handles category nesting as groups with subtotals.

    args:
      workbook: the name of the spreadsheet to load data into.
      target_sheet: the name of the tab to update. Either 'iande_actl' or'iande'
      df: the dataframe that has basic clean up already done
      force: Optional. True to override warning. Default False
      f_fcast: Optional. The first forecast year as Ynnnn. If none, will read from the workbook file. Default None.
      title_row: Optional. The row number in Excel for the title row (needed to compute subtotals). Default 1.
      verbose: True to report out all the lines that are in actl but not in iande. default False.

    returns:
      A dataframe and the groups (for folding)

    raises:
      FileNotFoundError: if workbook does not exist or the config file does not exist.
      ValueError: if tab_target is not iande or iande_actl
      IndexError: if columns expected and received from data source do not match
    '''

  if title_row!=1:
    raise NotImplementedError('Title row must be 1 for iande and iande_actl for now.')
  valid_sheets=['iande_actl','iande','current']
  heading_row=1+title_row
  if target_sheet not in valid_sheets:
    raise ValueError('tab_target must be one of: %s'%', '.join(valid_sheets))
  logger.debug('Preparing data for {}'.format(target_sheet))
  # get the workbook from file
  try:
    wb = load_workbook(filename = workbook, read_only=False, keep_vba=True)
    logger.debug('loaded workbook from {}'.format(workbook))
    config=read_config()
  except FileNotFoundError:
    raise FileNotFoundError(f'file not found {workbook}') from None
  if f_fcast is None:
    f_fcast='Y%d' % get_f_fcast_year(wb,config) # get the first forecast year from the general state table or config as available
  logger.debug ('First forecast year is: %s',f_fcast)

  tables=config['sheets'][target_sheet]['tables']
  assert len(tables)==1,'not exactly one table defined'
  tab_tgt=tables[0]['name']

  df=nest_by_cat(df) # creates key, leaf and level fields
  df=hier_insert(df,tables[0]) # insert any specified lines into hierarchy
  df=is_leaf(df)# mark rows that are leaves of the category tree
  groups=identify_groups(df)
  del df['level'] # clear out temp field

  expected_cols=set(columns_for_table(wb,target_sheet,tab_tgt,config).name)

  match target_sheet:
    case 'iande':
      del df['is_leaf'] # clear out temp field
      test_required_lines(df,workbook,f_fcast,initialize_iande=True,force=force,verbose=verbose) # raises error if not good.
      # adjust for iande, adding columns
      for y in range(int(f_fcast[1:]),config['end_year']+1): # add columns for forecast years
        df['Y{}'.format(y)]=None
      #use formulas to pull non-totals from iande_actl
      tr=this_row('Key') # syntax to refer to key on this row inside of Excel
      for rix,row in df.iterrows():
        for cix,col_name in enumerate(df.columns):
          if col_name[1:].isnumeric():
            val=row[col_name]
            if not isinstance(val,str):# if its a string then its formula for subtotal, so leave it
              if int(col_name[1:])<int(f_fcast[1:]): # but for actual items, refer to iande_actl
                cl=get_column_letter(1+cix)
                formula=f'=get_val({tr},"tbl_iande_actl",this_col_name())'.format()
                df.loc[rix,col_name]=formula
    case 'iande_actl':
      del df['is_leaf'] # clear out temp field
      test_required_lines(df,workbook,f_fcast,initialize_iande=False,force=force,verbose=verbose) # raises error if not good.
    case 'current':
      as_of=df.columns[-1]
      as_of_datetime=pd.to_datetime(as_of.split(' - ')[-1])
      assert as_of_datetime.year==int(f_fcast[1:]),'YTD file is not for first forecast year'
      yymmdd='%4d%02d%02d'%(as_of_datetime.year,as_of_datetime.month,as_of_datetime.day)
      df.rename(columns={as_of:yymmdd},inplace=True)
      expected_cols= (expected_cols-set(['YTD']))|set(['Y'+yymmdd]) 
      df[['Factor','Add']]=None
      formula='=IF(AND(ISBLANK([@Factor]),ISBLANK(@Add)),"",([@Y%s]*[@Factor])+[@Add])'%yymmdd
      df['Year']=table_ref(formula)
    

  df=y_year(df)  
  df=subtotal_formulas(df,groups,heading_row)

  data_has_cols=set(df.columns)
  if data_has_cols != expected_cols:
    msg='Columns expect does not match data source for {}'.format(tab_tgt)
    logger.error(msg)
    logger.error('Extra expected columns: {}, Extra received columns: {}'.format(expected_cols-data_has_cols,data_has_cols-expected_cols))
    raise IndexError(msg)

  return df,groups


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description ='Copies data from input file into tab "iande_actl" or "current" after doing some checks. ')
  parser.add_argument('-s','--sheet',choices=['iande_actl','current'],default='iande_actl',help='which sheet - iande_actl or current')
  parser.add_argument('-p','--path',default= None,help='The path and name of the input file. If not given will use "data/iande.tsv" or "data/iande_ytd.tsv" depending on sheet')
  parser.add_argument('-w','--workbook',default='data/test_wb.xlsm',help='Target workbook')# TODO fcast
  parser.add_argument('-f','--force', action='store_true', default=False, help='Use -f to ignore warning')
  
  args=parser.parse_args()
  path=args.path
  if path is None:
    path={'iande_actl':'data/iande.tsv','current':'data/iande_ytd.tsv'}[args.sheet]
  config=read_config()
  ffy=config['first_forecast_year']
  table_info=config['sheets'][args.sheet]['tables'][0]
  data=read_iande_actl(data_info={'path':path})
  table='tbl_'+args.sheet
  data,fold_groups=prepare_iande_actl(workbook=args.workbook,target_sheet=args.sheet,df=data,force=args.force,f_fcast='Y%04d'%ffy)
  data=forecast_formulas(table_info,data,ffy) # insert forecast formulas per config
  data=actual_formulas(table_info,data,ffy) # insert actual formulas per config
  wkb = load_workbook(filename = args.workbook, read_only=False, keep_vba=True)
  wkb=fresh_sheet(wkb,args.sheet)
  wkb= write_table(wkb,target_sheet=args.sheet,df=data,table_name=table,groups=fold_groups)
  attrs=col_attrs_for_sheet(wkb,args.sheet,read_config())
  wkb=set_col_attrs(wkb,args.sheet,attrs)
  wkb.save(args.workbook)
