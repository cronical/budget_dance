'''Utility to add tabs to the workbook and sets the tab colors

May be modified to add new tabs and re-run.  Does not replace or delete any tabs, only adds them
'''
import argparse
from os.path import exists
from openpyxl import load_workbook
from openpyxl.utils.cell import get_column_letter
from openpyxl.styles import Font
from openpyxl.worksheet.table import Table, TableStyleInfo
import yaml
from dance.util.logs import get_logger
from dance.setup.local_data import read_data
import remote_data



def first_not_hidden(tab_info):
  '''determine the first column that is not hidden (origin 1)'''
  if 'hidden' not in tab_info:
    return 1
  for col_no,col_data in enumerate(tab_info['columns']):
    if col_data['name'] in tab_info['hidden']:
      continue
    return col_no+1

def include_year(table_info,first_forecast_year,proposed_year):
  '''return True if proposed year should be displayed'''
  ao=False
  if 'actual_only' in table_info:
    ao=table_info['actual_only']
  if not ao:
    return True
  return first_forecast_year > proposed_year

def refresh_sheets(target):
  '''create or refresh tabs'''
  logger=get_logger(__file__)
  fn='dance/setup/setup.yaml'
  with open(fn) as y:
    config=yaml.load(y,yaml.Loader)
  logger.debug('read {} as config'.format(fn))

  year_columns=[f'Y{x}' for x in range(config['start_year'],1+config['end_year'])]
  wb=load_workbook(filename = target,keep_vba=True)
  sheets=wb.sheetnames
  logger.info('{} existing sheets in {}'.format(len(sheets),target))
  if 'Sheet' in sheets:
    del wb['Sheet']
    logger.info('Removed Sheet')

  table_map={}
  ffy=config['first_forecast_year']
  general_state={'first_forecast': f'Y{ffy}'}
  for sheet_group,sheet_group_info in config['sheet_groups'].items():
    for sheet_name,sheet_info in config['sheets'].items():
      if sheet_info['sheet_group'] != sheet_group:
        continue
      color=sheet_group_info['color']
      existing=False
      try:
        _=sheets.index(sheet_name) # is it already there?
        ws = wb[sheet_name]
        existing=True
      except ValueError:
        ws=wb.create_sheet(sheet_name)
        logger.info('sheet {} added'.format(sheet_name))
      ws.sheet_properties.tabColor= color
      if existing:
        logger.info('Sheet {} already exists, so not initializing'.format(sheet_name))
        continue

      # if new sheets write tables
      set_widths={}
      for table_info in sheet_info['tables']:

        #take specified or default row and column
        row=1
        if 'row' in table_info:
          row=table_info['row']
        start_col=1
        if 'start_col' in table_info:
          start_col=table_info['start_col']

        title_cell=f'{get_column_letter((start_col-1)+first_not_hidden(table_info))}{row}'
        ws[title_cell].value=table_info['title']
        ws[title_cell].font=Font(name='Calibri',size=16,color='4472C4')
        row+=1
        start_row=row # mark start of table

        col_defns=table_info['columns']
        col_count=len(col_defns)

        last_width=config['year_column_width'] # use the year column width as a default for 1st column
        for col_no,col_data in enumerate(col_defns):
          width=last_width # user prior column's width as default
          if 'width' in col_data:
            width=col_data['width']

          # if width already set from prior table use that
          if 1+col_no in set_widths:
            width=set_widths[1+col_no]
          else:
            set_widths[1+col_no]=width
          ws.column_dimensions[get_column_letter(start_col+col_no)].width=width

          # if any table marks this col as hidden it will be so for all tables
          if 'hidden' in table_info:
            ws.column_dimensions[get_column_letter(start_col+col_no)].hidden=col_data['name']in table_info['hidden']
          ws.cell(row=row,column=start_col+col_no,value=col_data['name'])
          last_width=width

        # if table has years add them
        if table_info['years']:
          include=[include_year(table_info,ffy,int(y[1:])) for y in year_columns]
          for x, y in enumerate(year_columns):
            if include[x]:
              ws.column_dimensions[get_column_letter(start_col+x+col_count)].width=config['year_column_width']
              ws.cell(row=start_row,column=start_col+len(col_defns)+x,value=y)
          col_count+=sum(include)

        # if table has a data source add those rows
        if 'data' in table_info:
          assert 'source' in table_info['data']
          data_info=table_info['data']
          valid_sources=['internal','remote','local']
          source=data_info['source']
          if source not in valid_sources:
            logger.error('Only the following are valid data sources {}'.format(valid_sources))
            quit()
          if source == 'internal':
            try:
              var_name=data_info['name']
              data=locals()[var_name]
            except KeyError:
              logger.error('configured internal data source {} does not exist.'.format(var_name))
              quit()
            if not isinstance(data,dict):
              logger.error('configured internal data source {} is not a dict.'.format(var_name))
              quit()
            if col_count !=2:
              logger.error('{} should have two columns to receive internal data'.format(table_name))
              quit()

          if source == 'remote':
            if 'api_key' in data_info:
              fn='./private/api_keys.yaml'
              if not exists(fn):
                logger.error('call for remote data but file {} does not exist'.format(fn))
                quit()
              with open(fn) as y:
                api_keys=yaml.load(y,yaml.Loader)
              key_name=data_info['api_key']
              if key_name not in api_keys:
                logger.error('call for remote data but api key name {} does not exist in {}'.format(key_name,fn))
                quit()
              data_info['api_key']=api_keys[key_name]
              logger.info('API key retrieved from private data')
            data=remote_data.request(data_info)
            logger.info('pulled data from remote')
          if source=='local':
            data=read_data(data_info)
          if isinstance(data,dict):
            for k,v in data.items():
              row+=1
              ws.cell(row=row,column=start_col).value=k
              ws.cell(row=row,column=start_col+1).value=v
          if isinstance(data,list):
            for values in data:
              row+=1
              for i,v in enumerate(values):
                ws.cell(row=row,column=start_col+i).value=v
        else: # if no data, just a blank row
          row+=1
        # make into a table
        top_left=f'{get_column_letter(start_col)}{start_row}'
        bot_right=f'{get_column_letter((start_col-1)+col_count)}{row}'
        rng=f'{top_left}:{bot_right}'
        table_name=table_info['name']
        tab = Table(displayName=table_name, ref=rng)
        style = TableStyleInfo(name=sheet_group_info['table_style'],  showRowStripes=True)# Add a builtin style with striped rows and banded columns
        tab.tableStyleInfo = style
        ws.add_table(tab)
        logger.info('  table {} added'.format(table_name))
        table_map[table_name]=sheet_name
      ws.sheet_view.zoomScale=config['zoom_scale']


  wb.save(filename=target)
  logger.info('workbook {} saved'.format(target))

if __name__=='__main__':
    # execute only if run as a script
  parser = argparse.ArgumentParser(description ='set tabs the given workbook')
  parser.add_argument('target_file', help='provide the name of the output file')
  args=parser.parse_args()
  refresh_sheets(args.target_file)
