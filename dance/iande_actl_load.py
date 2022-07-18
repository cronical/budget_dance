#! /usr/bin/env python
'''
Copies data from "data/iande.tsv" into tab "iande_actl" after doing some checks.
'''
import argparse

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

from dance.util.books import fresh_sheet
from dance.util.files import tsv_to_df, read_config
from dance.util.tables import df_for_table_name,get_value_for_key, this_row
from dance.util.logs import get_logger

logger=get_logger(__file__)

def test_required_lines(workbook,forecast_start_year,initialize_iande=False,force=False):
  ''' Test the proposed updates to income and expense, to keep iande and iande_actl aligned.
  Compute the list of required lines given the forecast start year in form y_year
  Args:
    df: the dataframe containing the proposed replacement for iande_actl
    workbook: the name of the target excel file
    forecast_start_year: The first forecast year as a String (Ynnnn)
    initialize_iande: True if we are going to (re)initialize iande. Default False.
    force: True if we are going to allow forecast values to be destroyed. Default False

  returns: the required lines and all lines as sets

  raises: ValueError when removing non-zero forecast lines without the -f (force) flag

  '''
  iande=df_for_table_name(table_name='tbl_iande',workbook=workbook)
  cols= list(iande)
  ix=cols.index(forecast_start_year)
  c=cols[ix:]

  def not_all_are_empty(a):
    return any([x is not None for x in list(a)])

  req_lines=set(iande.index[iande[c].apply(not_all_are_empty,axis=1)])
  # make sure nothing of the forecast gets lost due to changed lines.

  keys=list(iande_actl['key'])
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
    logger.info('Note: new lines (will be in iande_actl but not in iande, but you can manually add them there')
    logger.info('Note: lines with the suffix "-Other" occur when a transaction exists at a non-leaf in the category tree')
    logger.info('      If not desired, remove transaction and run again.  ')
  for nw in new:
    logger.info('   {}'.format(nw))

def indent_other(str):
  '''indent -other rows to fix an anomoly in the md report
  '''
  if -1==str.find('-Other'):
    return str
  else:
    return '   '+str

def ravel(pathparts):
  '''create the real key field'''
  path=''
  for pp in pathparts:
    if len(path)>0: path=path +':'
    path=path+pp
  return path

def read_iande_actl():
  '''
  Read data from 'data/iande.tsv' into a dataframe, creating key of nested category names

  returns: dataframe which includes column 'level', to be removed later before inserting into wb
  raises: FileNotFoundError
  '''
  input_file='data/iande.tsv'

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

  # determine level of each row in the category hierarchy
  # hold the flat view in the key column for now
  df.insert(loc=0,column='key',value=df.Account.str.lstrip()) # a temporary value - used to define level
  #create a level indicator
  # re-use the totals colum
  df.rename(columns={'Total':'level'},inplace=True)
  df['level']=((df.Account.str.len() - df.key.str.len()))/3
  df['level']=level=[int(x) for x in df.level.tolist()]


  keys=[]
  keyparts=df.Account.tolist()
  rows=list(range(0,len(level))) # rows and columns are origin 0, excel uses origin 1 plus it contains the headings so for rows its off by 2
  last_level=-1
  for rw in rows:
    lev=level[rw]
    if 0==lev:
      pathparts=[]
    else:
      if lev > last_level:
        pathparts.append(keyparts[rw-1].strip())
      if lev < last_level:
        pathparts=pathparts[:-1]
    a=pathparts.copy()
    a.append(keyparts[rw].strip())
    key=ravel(a)
    assert key==':'.join(a),'hmm they are not the same'
    keys.append(key)
    last_level=lev

  df['key']=keys

  # change the year columns to Y+year format
  for cn in df.columns.values.tolist():
    try:
      n=int(cn)
      nn = 'Y{}'.format(n)
      df.rename(columns={cn:nn},inplace=True)
    except ValueError:
      n=0
  return df

def prepare_iande_actl(df,workbook,target_sheet,force=False,f_fcast=None):
  '''prepare the dataframe for insertion into workbook
    Makes checks to ensure nothing of the forecast gets lost due to changed lines.
    Checks can be overridden by a flag.
    Handles category nesting as groups with subtotals.


    args:
    workbook: the name of the spreadsheet to load data into.
    target_sheet: the name of the tab to update. Either 'iande_actl' or'iande'
    force: Optional, True to override warning. Default False
    ffy: The first forecast year as Ynnnn. If none, will read from the workbook file. Default None.

    raises:
      FileNotFoundError: if workbook does not exist or the config file does not exist.
      ValueError: if tab_target is not iande or iande_actl


    '''

  valid_sheets=['iande_actl','iande']
  if target_sheet not in valid_sheets:
    raise ValueError('tab_target must be iande or iande_actl')
  initialize_iande=target_sheet='iande'
  # get the workbook from file
  try:
    wb = load_workbook(filename = workbook, read_only=False, keep_vba=True)
    logger.info('loaded workbook from {}'.format(workbook))
    config=read_config()
  except FileNotFoundError as e:
    raise f'file not found {workbook}' from e
  if f_fcast is None:
    f_fcst=get_value_for_key(wb,'first_forecast') # get the first forecast year from the general state table
  logger.info ('First forecast year is: %s',f_fcst)

  test_required_lines(workbook,f_fcast,initialize_iande=initialize_iande,force=force) # raises error if not good.

  def getlev (e):
    '''utility to aid with setting up groups'''
    return e[0]

  # copy the data in to enabled tabs in file and into table, set up subtotals and groups

  sg=config['sheets'][target_sheet]['sheet_group']
  tab_style=config['sheet_groups'][sg]['table_style']
  tables=config['sheets'][target_sheet]['tables']
  assert len(tables)==1,'too many tables'
  tab_tgt=tables[0]['name']

  old_df=df_for_table_name(tab_tgt,workbook,data_only=True)
  old_cols=list(old_df.columns)
  if target_sheet=='iande_actl':
    assert old_cols==list(df.columns),'column names in file do not match update'
  if target_sheet=='iande':
    ixs=[old_cols.index(c) for c in df.columns]
    assert ixs==list(range(len(df.columns))),'update column names are not all in existing tab in order'
    future_columns=[cn for cn in old_cols if cn not in df.columns] # create future columns
    tr=this_row('Key')
    for x,c in enumerate(future_columns):
      cl=get_column_letter(len(old_cols)+x)
      val=f'=get_val({tr},"tbl_iande_actl",{cl}$2)'.format()
      df[c]=[val]*len(df)

  wb=fresh_sheet(wb,target_sheet)
  ws=wb[target_sheet]
  cols=df.columns

  # put in subtotal formulas for the numeric columns
  # the subtotals are aligned with the groups, so do those too
  #whenever the level goes down from the previous level its a total
  groups=[] # level, start, end
  last_level=-1
  keys=list(df['key'])
  for ix,row in df.iterrows():
    level_change= row['level']-last_level
    k=row['Key']# get the key value from the file
    if level_change <0: #this should be a total line
      n=k.find(' - TOTAL') # see if it has the total label
      assert -1 != n # if not we are in trouble
      bare = k[:n]# # remove the total label
      try:
        x=keys.index(bare) # look for this in the keys - should be there
        #since we have the row for the section start - we'll blank out those zeros
        # TODO move the formatting logic to the spreadsheet load section
        #for cl in cols:
        #  ws.cell(column=cl+1,row=x+2).number_format='###'
        # prepare the grouping specs
        groups.append([row['level']+1,x+2,ix+1])
      except ValueError:
        assert False, '{} not found in keys'.format(k)
      # now replace the hard values with formulas
      # if its not a total just let the value stay there
      for cx,cl in enumerate(cols):
        if cl.startswith('Y'):
          let=get_column_letter(cx+1)
          formula='=subtotal(9,{}{}:{}{})'.format(let,x+2,let,row+1)
          df.loc[ix,[cl]]=formula

    if -1!=k.find('TOTAL INCOME - EXPENSES'): # we are on the last row
      x=keys.index('Income - TOTAL')
      for cx,cl in enumerate(cols):
        if cl.startswith('Y'):
          let=get_column_letter(cx+1)
          formula='={}{}-{}{}'.format(let,x+2,let,row+1)
          df.loc[ix[cl]]=formula
    #for all cells apply formats
    last_level=row['level']

  # set up the row groups highest level to lowest level
  # outline levels are +1 to our levels here
  # 0 here = 1 in Excel - such as Income, Expense
  # 1 here = 2 in Excel - such as I, T and X

  groups.sort(key=getlev)
  for grp in groups:
    ws.row_dimensions.group(grp[1],grp[2],outline_level=grp[0], hidden=grp[0]>2)

  rng=ws.dimensions
  tab = Table(displayName=tab_tgt, ref=rng)
  # Add a builtin style with striped rows and banded columns
  # The styles are seen on the table tab in excel broken into Light, Medium and Dark.
  # The number seems to be the index in that list (top to bottom, left to right, origin 1)
  style = TableStyleInfo(name=tab_style,  showRowStripes=True)
  tab.tableStyleInfo = style
  ws.add_table(tab)
  logger.info('table {} added'.format(target_sheet))

  wb.save(workbook)
  logger.info('saved to {}'.format(workbook))

  # ws.column_dimensions.group('A','A', hidden=True)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description ='Copies data from "data/iande.tsv" into tab "iande_actl" after doing some checks. ')
  parser.add_argument('--workbook','-w',default='data/fcast.xlsm',help='Target workbook')
  parser.add_argument('--sheet','-s',default='iande_actl',help='which sheet - iande or iande_actl')
  parser.add_argument('--force', '-f',action='store_true', help='Use -f to ignore warning')
  parser.add_argument('--ffy', '-y',help='first forecast year. Must be provided if workbook does not have value. Default None.')
  args=parser.parse_args()
  iande_actl=read_iande_actl()
  prepare_iande_actl(iande_actl,workbook=args.workbook,target_sheet=args.sheet,force=args.force,f_fcast=args.ffy)
  