#! /usr/bin/env python
'''
Copies data from "data/iande.tsv" into tab "iande_actl" after doing some checks.
'''
import argparse

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


from dance.util.books import col_attrs_for_sheet, set_col_attrs, fresh_sheet
from dance.util.files import tsv_to_df, read_config
from dance.util.tables import df_for_table_name, this_row, write_table, get_f_fcast_year,columns_for_table
from dance.util.logs import get_logger
from dance.ira_distr import ira_distr_summary

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
  logger.info('Testing required lines')
  try:
    iande=df_for_table_name(table_name='tbl_iande',workbook=workbook)
  except ValueError as err:
    logger.info(str(err))
    logger.info('Unable to check required lines')
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
    logger.info('All forecast items are included in input file.')

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

  # special handling for IRA-Txbl-Distr

  for ix,_ in df.loc[df.Account.str.contains('IRA-Txbl-Distr')].iterrows(): # zero or one rows
    itd=ira_distr_summary().loc['Amount']
    for y in itd.index:
      df.loc[ix,y[1:]]=itd[y]


  # change the year columns to Y+year format
  for cn in df.columns.values.tolist():
    if cn.isnumeric():
      n=int(cn)
      nn = 'Y{}'.format(n)
      df.rename(columns={cn:nn},inplace=True)

  df.reset_index(drop=True,inplace=True)
  return df

def prepare_iande_actl(workbook,target_sheet,df,force=False,f_fcast=None,verbose=False):
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
      verbose: True to report out all the lines that are in actl but not in iande. default False.

    returns:
      A dataframe and the groups (for folding)

    raises:
      FileNotFoundError: if workbook does not exist or the config file does not exist.
      ValueError: if tab_target is not iande or iande_actl
      IndexError: if columns expected and received from data source do not match
    '''

  valid_sheets=['iande_actl','iande']
  if target_sheet not in valid_sheets:
    raise ValueError('tab_target must be iande or iande_actl')
  logger.info('Preparing data for {}'.format(target_sheet))
  initialize_iande=target_sheet=='iande'
  # get the workbook from file
  try:
    wb = load_workbook(filename = workbook, read_only=False, keep_vba=True)
    logger.info('loaded workbook from {}'.format(workbook))
    config=read_config()
  except FileNotFoundError:
    raise FileNotFoundError(f'file not found {workbook}') from None
  if f_fcast is None:
    f_fcast='Y%d'% get_f_fcast_year(wb,config) # get the first forecast year from the general state table or config as available
  logger.info ('First forecast year is: %s',f_fcast)

  tables=config['sheets'][target_sheet]['tables']
  assert len(tables)==1,'not exactly one table defined'
  tab_tgt=tables[0]['name']

  # creating key of nested category names
  # determine level of each row in the category hierarchy
  # hold the flat view in the key column for now
  df.insert(loc=0,column='Key',value=df.Account.str.lstrip()) # used to define level
  #create a level indicator, re-use the totals column which for 'level', to be removed later before inserting into wb
  df.rename(columns={'Total':'level'},inplace=True)
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

  # put in subtotal formulas for the numeric columns
  # the subtotals are aligned with the groups, so do those too
  #whenever the level goes down from the previous level its a total
  groups=[] # level, start, end
  last_level=-1
  keys=list(df['Key'])
  for ix,row in df.iterrows():
    level_change= row['level']-last_level
    k=row['Key']# get the key value from the file
    if level_change <0: #this should be a total line
      n=k.find(' - TOTAL') # see if it has the total label
      assert -1 != n # if not we are in trouble
      bare = k[:n]# # remove the total label
      try:
        # prepare the grouping specs
        bx=keys.index(bare) # look for this in the keys - should be there
        groups.append([row['level']+1,bx+3,ix+2])
      except ValueError as e:
        raise ValueError(f'{k} not found in keys'.format()) from e
    last_level=row['level']
  del df['level'] # clear out temp field

  test_required_lines(df,workbook,f_fcast,initialize_iande=initialize_iande,force=force,verbose=verbose) # raises error if not good.

  if target_sheet=='iande': # adjust for iande, adding columns
    for y in range(f_fcast,config['end_year']+1): # add columns for future years
      df['Y{}'.format(y)]=None

  # now replace the hard values with formulas
  # if its not a total just let the value stay there
  for group in groups:
    for cx,cl in enumerate(df.columns):
      if cl.startswith('Y'):
        let=get_column_letter(cx+1)
        formula='=subtotal(9,{}{}:{}{})'.format(let,group[1],let,group[2])
        df.loc[group[2]-2,[cl]]=formula

  if -1!=k.find('TOTAL INCOME - EXPENSES'): # we are on the last row
    group=groups[-1]
    ix=keys.index('Income - TOTAL')
    y=keys.index('Expenses - TOTAL')
    for cx,cl in enumerate(df.columns):
      if cl.startswith('Y'):
        let=get_column_letter(cx+1)
        formula='={}{}-{}{}'.format(let,group[1],let,y+3)
        df.loc[ix,[cl]]=formula

  cols_df=columns_for_table(wb,target_sheet,tab_tgt,config)
  expected=set(cols_df.name)
  data_has=set(df.columns)
  if data_has != expected:
    msg='Columns expect does not match data source for {}'.format(tab_tgt)
    logger.error(msg)
    logger.error('Extra expected columns: {}, Extra received columns: {}'.format(expected-data_has,data_has-expected))
    raise IndexError(msg)

  if target_sheet=='iande': # adjust for iande, using formulas to pull non-totals from iande_actl
    tr=this_row('Key') # syntax to refer to key on this row inside of Excel
#    for ix,c in cols_df.iterrows():# use formulas for actual columns
#      col_name=c['name']
#      if col_name[1:].isnumeric():
#        if int(col_name[1:])<f_fcast: # only actual items
#          cl=get_column_letter(1+ix)
#          formula=f'=get_val({tr},"tbl_iande_actl",{cl}$2)'.format()
#          df[col_name]=[formula]*df.shape[0]

    for rix,row in df.iterrows():
      for cix,col_name in enumerate(df.columns):
        if col_name[1:].isnumeric():
          val=row[col_name]
          if not isinstance(val,str):# if its a string then its formula for subtotal, so leave it
            if int(col_name[1:])<f_fcast: # but for actual items, refer to iande_actl
              cl=get_column_letter(1+cix)
              formula=f'=get_val({tr},"tbl_iande_actl",{cl}$2)'.format()
              df.loc[rix,col_name]=formula
      pass
  return df,groups


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description ='Copies data from input file into tab "iande_actl" after doing some checks. ')
  parser.add_argument('--workbook','-w',default='data/fcast.xlsm',help='Target workbook')
  parser.add_argument('--path','-p',default= 'data/iande.tsv',help='The path and name of the input file')
  parser.add_argument('--sheet','-s',default='iande_actl',help='which sheet - iande or iande_actl')
  parser.add_argument('--force', '-f',action='store_true', default=False, help='Use -f to ignore warning')
  parser.add_argument('--ffy', '-y',help='first forecast year. Must be provided if workbook does not have value. Default None.')
  args=parser.parse_args()
  iande_actl=read_iande_actl(data_info={'path':args.path})
  table='tbl_'+args.sheet
  iande_actl,fold_groups=prepare_iande_actl(workbook=args.workbook,target_sheet=args.sheet,df=iande_actl,force=args.force,f_fcast=args.ffy)
  wkb = load_workbook(filename = args.workbook, read_only=False, keep_vba=True)
  wkb=fresh_sheet(wkb,args.sheet)
  wkb= write_table(wkb,target_sheet=args.sheet,df=iande_actl,table_name=table,groups=fold_groups)
  attrs=col_attrs_for_sheet(wkb,args.sheet,read_config())
  wkb=set_col_attrs(wkb,args.sheet,attrs)
  wkb.save(args.workbook)
