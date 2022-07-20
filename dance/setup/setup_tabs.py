'''Utility to add tabs to the workbook and sets the tab colors

May be modified to add new tabs and re-run.  Unless overwrite is selected, does not replace or delete any tabs, only adds them
'''
import argparse
from os.path import exists
from openpyxl import load_workbook
from openpyxl.utils.cell import get_column_letter
from openpyxl.styles import Font
import pandas as pd
import yaml
from dance.util.logs import get_logger
from dance.setup.local_data import read_data
from dance.util.files import read_config
from dance.util.tables import first_not_hidden,write_table
import remote_data

def include_year(table_info,first_forecast_year,proposed_year):
  '''return True if proposed year should be displayed'''
  ao=False
  if 'actual_only' in table_info:
    ao=table_info['actual_only']
  if not ao:
    return True
  return first_forecast_year > proposed_year

def refresh_sheets(target_file,overwrite=False):
  '''create or refresh tabs'''
  logger=get_logger(__file__)
  config=read_config()
  years=range(config['start_year'],1+config['end_year'])
  all_year_columns=[f'Y{x}' for x in years] # all the years, some tables may have only actual
  wb=load_workbook(filename = target_file,keep_vba=True)
  sheets=wb.sheetnames
  logger.info('{} existing sheets in {}'.format(len(sheets),target_file))

  for default_name in 'Sheet','Sheet1','Sheet2','Sheet3':
    if default_name in sheets:
      del wb[default_name]
      logger.info('Removed "{}"'.format(default_name))

  table_map={} # build list of tables and which sheet they are on
  ffy=config['first_forecast_year']
  general_state={'first_forecast': f'Y{ffy}',
    'bank_interest':config['bank_interest']}
  _=general_state # it is used by referencing locals(), but pylance can't figure it out

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
        if not overwrite:
          logger.info('Sheet {} already exists, so not initializing'.format(sheet_name))
          continue
        else:
          del wb[sheet_name]
          ws=wb.create_sheet(sheet_name)
          logger.info('sheet {} deleted and recreated'.format(sheet_name))

      # if new sheets write tables
      set_widths={}
      for table_info in sheet_info['tables']:

        #take specified or default items
        key_values={'title_row':1,'start_col':1,'include_years':False}
        for k in key_values:
          if k in table_info:
            key_values[k]=table_info[k]

        title_cell=f'{get_column_letter((key_values["start_col"]-1)+first_not_hidden(table_info))}{key_values["title_row"]}'
        ws[title_cell].value=table_info['title']
        ws[title_cell].font=Font(name='Calibri',size=16,color='4472C4')
        row=key_values['title_row']+1
        table_start_row=row # mark start of table

        col_defns=table_info['columns']
        col_count=len(col_defns)
        all_columns=col_defns # TODO come back and add the years


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
          ws.column_dimensions[get_column_letter(key_values['start_col']+col_no)].width=width

          # if any table marks this col as hidden it will be so for all tables
          if 'hidden' in table_info:
            ws.column_dimensions[get_column_letter(key_values['start_col']+col_no)].hidden=col_data['name']in table_info['hidden']
          ws.cell(row=row,column=key_values['start_col']+col_no,value=col_data['name'])
          last_width=width

        # if table has years, determine which ones are for this table
        # (if actual only, just the actual years)
        table_year_columns=[]
        if key_values['include_years']:
          for y in all_year_columns:
            if not include_year(table_info,ffy,int(y[1:])):
              continue
            table_year_columns+=[y]
          for x, y in enumerate(table_year_columns):
            ws.column_dimensions[get_column_letter(key_values['start_col']+x+col_count)].width=config['year_column_width']
            ws.cell(row=table_start_row,column=key_values['start_col']+len(col_defns)+x,value=y)
          col_count+=len(table_year_columns)

        groups=None
        # if table has a data source add those rows
        if 'data' not in table_info:
          data=pd.DataFrame([None]*col_count,columns=all_columns) # a row of blanks if no data is provided
        else:
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
              logger.error('{} should have two columns to receive internal data'.format(table_info['name']))
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
            data,groups=read_data(data_info,years,ffy,target_file=target_file)
          if isinstance(data,dict):
            data=pd.DataFrame([(k,v) for k,v in data.items()],columns=all_columns)
          if isinstance(data,list):
            data=pd.DataFrame(list,columns=all_columns)
          if isinstance(data,pd.DataFrame):
            pass
        write_table(workbook=target_file,target_sheet=sheet_name,table_name=table_info['name'],df=data,groups=groups)


        logger.info('  table {} added'.format(table_info['name']))
        wb.save(filename=target_file) # save after each sheet to allow successive sheets to locate earlier sheet data
        logger.info('workbook {} saved'.format(target_file))
        table_map[table_info['name']]=sheet_name
      ws.sheet_view.zoomScale=config['zoom_scale']


  wb.save(filename=target_file)
  logger.info('workbook {} saved'.format(target_file))

if __name__=='__main__':
    # execute only if run as a script
  parser = argparse.ArgumentParser(description ='set tabs the given workbook')
  parser.add_argument('target_file', help='provide the name of the output file')
  args=parser.parse_args()
  refresh_sheets(args.target_file)
