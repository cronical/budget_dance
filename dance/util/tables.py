'''Utilities dealing with worksheet tables.'''
import pandas as pd
from openpyxl import load_workbook
import openpyxl.utils.cell
from dance.util.logs import get_logger


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

def df_for_table_name(table_name=None, workbook='data/fcast.xlsm',data_only=False):
  '''Opens the file, and extracts a table as a dataFrame with the first column as the dataframe index'''
  logger=get_logger(__file__)
  wb = load_workbook(filename = workbook, read_only=False, keep_vba=True, data_only=data_only)
  ws=wb['utility']
  ref=ws.tables['tbl_table_map'].ref
  table_map = df_for_range(worksheet=ws,range_ref=ref)
  ws_name =ws_for_table_name(table_map=table_map, table_name=table_name)
  ws=wb[ws_name]
  table=df_for_range(worksheet=ws,range_ref=ws.tables[table_name].ref)
  logger.info('Loaded worksheet {} from {}'.format(ws_name,workbook))
  logger.info('{} rows and {} columns'.format(table.shape[0],table.shape[1]))
  return table

def df_for_table_name_for_update(table_name=None):
  '''Opens the file, and extracts a table as a dataFrame with the first column as the dataframe index
  returns dataframe, worksheet, range_ref and workbook
  since its going to be updated don't allow data only '''
  logger=get_logger(__file__)
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
  # get a value from the general state table
  ws=wb['utility']
  ref=ws.tables['tbl_table_map'].ref
  table_map = df_for_range(worksheet=ws,range_ref=ref)
  table_name='tbl_gen_state'
  ws_name =ws_for_table_name(table_map=table_map, table_name=table_name)
  ws=wb[ws_name]
  table=df_for_range(worksheet=ws,range_ref=ws.tables[table_name].ref)
  f_fcst= get_val(table,line_key=key,col_name='Value')
  return f_fcst

def this_row(field):
  ''' prepare part of the formula so support Excel;s preference for the [#this row] style over the direct @
  '''
  return '[[#this row],[{}]]'.format(field)
  