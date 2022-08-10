'''Utilities dealing with worksheet tables.'''
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from openpyxl.styles.numbers import BUILTIN_FORMATS,FORMAT_PERCENTAGE_00
from openpyxl.utils import get_column_letter

import openpyxl.utils.cell
from openpyxl.worksheet.table import Table, TableStyleInfo

from dance.util.logs import get_logger
from dance.util.files import read_config

logger=get_logger(__file__)

def df_for_range(worksheet=None,range_ref=None):
  '''get a dataframe given a range reference on a worksheet'''

  data=[]
  rb=openpyxl.utils.cell.range_boundaries(range_ref)
  for src_row in worksheet.iter_rows(min_col=rb[0],min_row=rb[1], max_col=rb[2], max_row=rb[3]):
    row=[]
    for cell in src_row:
      row.append(cell.value)
    data.append(row)

  cols = data[0][1:]
  idx = [r[0] for r in data[1:]]
  data = [r[1:] for r in data[1:]]
  df = pd.DataFrame(data, index=idx, columns=cols)
  return df

def ws_for_table_name(table_map=None,table_name=None):
  '''Return name of worksheet holding table given a data frame holding the table'''

  return table_map.loc[table_name,'Worksheet']

def df_for_table_name(table_name=None, workbook='data/fcast.xlsm',data_only=False,table_map=None):
  '''Opens the file, and extracts a table as a Pandas dataframe

  args:
    table_name:
    workbook:
    data_only: True to get the data not the formula
    table_map: in case the utility tab is not yet available, provide a dict mapping tables to worksheets

  returns: a dataFrame with the first column as the dataframe index

  raises:
    ValueError: when the file does not exist or its structures are not right

  '''
  try:
    wb = load_workbook(filename = workbook, read_only=False, keep_vba=True, data_only=data_only)
    if table_map is None:
      ws=wb['utility']
      ref=ws.tables['tbl_table_map'].ref
      table_map = df_for_range(worksheet=ws,range_ref=ref)
    else: # convert working form to stored form
      table_map=pd.DataFrame([(k,v) for k,v in table_map.items()],columns=['Table','Worksheet'])
      table_map.set_index('Table',inplace=True)
    ws_name =ws_for_table_name(table_map=table_map, table_name=table_name)
    ws=wb[ws_name]
    table=df_for_range(worksheet=ws,range_ref=ws.tables[table_name].ref)
  except (FileNotFoundError,KeyError):
    raise ValueError('workbook({}), worksheet({}) or internal structures not available'.format(workbook,table_name)) from None
  logger.info('Read table {} from {}'.format(table_name,workbook))
  logger.info('  {} rows and {} columns'.format(table.shape[0],table.shape[1]))
  return table

def df_for_table_name_for_update(table_name=None):
  '''Opens the file, and extracts a table as a dataFrame with the first column as the dataframe index
  returns dataframe, worksheet, range_ref and workbook
  since its going to be updated don't allow data only '''
  source='data/fcast.xlsm'
  wb = load_workbook(filename = source, read_only=False, keep_vba=True)
  logger.info('Loaded workbook from {}'.format(source))
  ws=wb['utility']
  ref=ws.tables['tbl_table_map'].ref
  table_map = df_for_range(worksheet=ws,range_ref=ref)
  ws_name =ws_for_table_name(table_map=table_map, table_name=table_name)
  ws=wb[ws_name]
  table=df_for_range(worksheet=ws,range_ref=ws.tables[table_name].ref)
  logger.info('{} rows and {} columns in sheet {}'.format(table.shape[0],table.shape[1],ws))
  return table, ws,ws.tables[table_name].ref,wb

def get_val(frame, line_key ,  col_name):
  '''get a single value from a dataframe'''
  return frame.loc[line_key,col_name]

def put_val(frame, line_key ,  col_name, value):
  '''Put a single value into a dataframe'''
  frame.loc[line_key,col_name]=value

def get_value_for_key(wb,key):
  '''Get a value from the general state table

  args:
    wb: the openpyxl workbook
    key: an item in the general (state) table

  returns: the value from the generate (state) table

  raises:
    ValueError: in case the structure in the file is not yet in place or the key is missing.
    Oddly ValueError works but KeyError does nothing.
  '''

  try:
    ws=wb['utility']
    ref=ws.tables['tbl_table_map'].ref
    table_map = df_for_range(worksheet=ws,range_ref=ref)
    table_name='tbl_gen_state'
    ws_name =ws_for_table_name(table_map=table_map, table_name=table_name)
    ws=wb[ws_name]
    table=df_for_range(worksheet=ws,range_ref=ws.tables[table_name].ref)
    value= get_val(table,line_key=key,col_name='Value')
    return value
  except KeyError as err:
    raise ValueError(str(err)) from None

def get_f_fcast_year(wb,config):
  '''get the first forecast year, using the value from the workbook if available, otherwise from the config

  args:
    wb: the workbook
    config: the config dict

  returns: integer year which is the first forecast
  '''
  ffy=None
  try:
    ffy=get_value_for_key(wb,'first_forecast')
    ffy=int(ffy[1:])
  except ValueError:
    ffy=config['first_forecast_year']
  return ffy

def this_row(field):
  ''' prepare part of the formula so support Excel;s preference for the [#this row] style over the direct @
  '''
  return '[[#this row],[{}]]'.format(field)

def first_not_hidden(table_info):
  '''determine the first column that is not hidden (origin 1)'''
  if 'hidden' not in table_info:
    return 1
  for col_no,col_data in enumerate(table_info['columns']):
    if col_data['name'] in table_info['hidden']:
      continue
    return col_no+1

def write_table(wb,target_sheet,table_name,df,groups=None):
  '''Write the dataframe to the worksheet, including the columns,
  add folding based on groups if given, format numbers, and make into a table.
  Reads the config file to determine some values.

  args:
    wb: the openpyxl workbook to write to
    target_sheet: the name of the worksheet in the workbook
    table_name: the name of the table to write into the target_sheet
    df: The prepared dataframe that has the correct columns
    groups: a list of 3 element lists, each representing a grouping. The elements are level, start, end

  returns: the workbook

  raises: IndexError if table not in config for the given sheet
  '''
  df.reset_index(drop=True,inplace=True) # rely on the index to figure row on sheet.
  try:
    config=read_config()
  except FileNotFoundError as e:
    raise FileNotFoundError('workbook or config file not found ') from e
  tables=config['sheets'][target_sheet]['tables']
  tx=[table_info['name'] for table_info in tables].index(table_name)
  sg=config['sheets'][target_sheet]['sheet_group']
  table_style=config['sheet_groups'][sg]['table_style']
  try:
    table_info=tables[tx]
  except IndexError as e:
    raise IndexError('Bad table reference: {}'.format(table_name)) from e

  key_values={'title_row':1,'start_col':1,'include_years':False}
  for k in key_values:   #take specified or default items
    if k in table_info:
      key_values[k]=table_info[k]

  title_cell=f'{get_column_letter((key_values["start_col"]-1)+first_not_hidden(table_info))}{key_values["title_row"]}'

  ws=wb[target_sheet]
  ws[title_cell].value=table_info['title']
  ws[title_cell].font=Font(name='Calibri',size=16,color='4472C4')
  table_start_row=key_values['title_row']+1 # the heading of the table (normally excel row 2 )
  table_start_col=key_values['start_col']

  col_defs=pd.DataFrame(table_info['columns']).set_index('name') # column name is index, attributes are columns

  # Place the headings
  for cx,cn in enumerate( df.columns):
    ws.cell(table_start_row,column=table_start_col+cx).value=cn
  # place the values
  fin_format=BUILTIN_FORMATS[41] #'#,###,##0;(#,###,##0);"-"?'
  for ix,values in df.iterrows(): # the indexes (starting at zero), and the data values
    for cx,cn in enumerate( df.columns):
      if cn in values:
        rix=ix+table_start_row+1
        cix=table_start_col+cx
        ws.cell(row=rix,column=cix).value=values[cn]
        if cn.startswith('Y')and cn[1:].isnumeric(): # formats for Y columns
          if 'ValType' in values:
            if values['ValType']=='Rate':
              ws.cell(row=rix,column=cix).number_format=FORMAT_PERCENTAGE_00
              continue
          # if not overridden use the fin format
          ws.cell(row=rix ,column=cix).number_format=fin_format

        else: # the non year columns
          if 'horiz' in col_defs.columns:
            horiz=col_defs.loc[cn].horiz
            if pd.notna(horiz):
              ws.cell(row=rix,column=cix).alignment = Alignment(horizontal=horiz)
          if 'number_format' in col_defs.columns: # number formats for non years.
            num_fmt=col_defs.loc[cn].number_format
            if pd.notna(num_fmt):
              if not isinstance(num_fmt,str):
                num_fmt=BUILTIN_FORMATS[num_fmt]  
              ws.cell(row=rix,column=cix).number_format=num_fmt



  if groups is not None: # the folding groups
    # set up the row groups highest level to lowest level
    # outline levels are +1 to our levels here
    # 0 here = 1 in Excel - such as Income, Expense
    # 1 here = 2 in Excel - such as I, T and X

    def getlev (e):
      '''utility to aid with setting up groups'''
      return e[0]
    groups.sort(key=getlev)
    for grp in groups:
      # use the start of the group to blank out numeric columns
      for cix,cn in enumerate(df.columns):
        if cn[0]=='Y':
          ws.cell(row=1+table_start_row+grp[1],column=table_start_col+cix).number_format='###'
      ws.row_dimensions.group(grp[1],grp[2],outline_level=grp[0], hidden=grp[0]>2)

  # making the table

  top_left=f'{get_column_letter(key_values["start_col"])}{table_start_row}'
  bot_right=f'{get_column_letter((key_values["start_col"]-1)+df.shape[1])}{table_start_row+df.shape[0]}'
  rng=f'{top_left}:{bot_right}'
  tab = Table(displayName=table_info['name'], ref=rng)
  # Add a builtin style with striped rows and banded columns
  # The styles are seen on the table tab in excel broken into Light, Medium and Dark.
  # The number seems to be the index in that list (top to bottom, left to right, origin 1)
  tab.tableStyleInfo = TableStyleInfo(name=table_style,  showRowStripes=True)
  ws.add_table(tab)
  logger.info('table {} added to {}'.format(table_info['name'],target_sheet))

  return wb

def columns_for_table(wb,sheet,table_name,config):
  '''Get the column definitions for a table based on the config

  args:
    wb: the name of the workbook which may hold the correct first forecast year,
      but if its not there, we get it from the config.
    sheet: the name of the sheet where the table is
    table_name: table name, like 'tbl_x_x'
    config: the config dict

  returns:
    A pandas dataframe with the name of the columns and attributes as columns
    The index can be used with an offset to locate the table on the worksheet.  The first index is zero.

  '''
  ffy=get_f_fcast_year(wb,config)
  for table_info in config['sheets'][sheet]['tables']:
    if table_info['name']!=table_name:
      continue
    years=range(config['start_year'],config['end_year']+1)
    # limit years as needed for actual only
    ao=False
    if 'actual_only' in table_info:
      ao = table_info['actual_only']
    if ao:
      years=[y for y in years if y < ffy]
    years=['Y{}'.format(y) for y in years]
    col_defs=[{'name':'default','width':config['year_column_width']}]
    col_defs+=table_info['columns']
    iy=False
    if 'include_years' in table_info:
      iy=table_info['include_years']
    if iy:
      for y in years:
        col_defs.append({'name':y,'width':config['year_column_width']})
    df=pd.DataFrame(col_defs)
    df=pd.DataFrame.fillna(df,method='ffill') # forward fill missing values
    df.width=df.width.astype(int)
    df=df.drop(0) # remove the default
    df.reset_index(drop=True,inplace=True)
    hide_these=[]
    if 'hidden' in table_info:
      hide_these=table_info['hidden']
    df['hidden']= df.name.isin(hide_these)
    return df
