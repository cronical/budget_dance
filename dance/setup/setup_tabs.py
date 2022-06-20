"""Utility to add tabs to the workbook and sets the tab colors

May be modified to add new tabs and re-run.  Does not replace or delete any tabs, only adds them
"""
import argparse
from openpyxl import load_workbook
from openpyxl.utils.cell import get_column_letter
from openpyxl.styles import Font
from openpyxl.worksheet.table import Table, TableStyleInfo
import yaml
from dance.util.logs import get_logger

def first_not_hidden(tab_info):
  '''determine the first column that is not hidden (origin 1)'''
  if 'hidden' not in tab_info:
    return 1
  for col_no,col_data in enumerate(tab_info['columns']):
    if col_data['name'] in tab_info['hidden']:
      continue
    return col_no+1


def refresh_sheets(target):
  '''create or refresh tabs'''
  logger=get_logger(__file__)
  fn='dance/setup/setup.yaml'
  with open(fn) as y:
    config=yaml.load(y,yaml.Loader)
  logger.debug(f'read {fn} as config')

  year_columns=[f'Y{x}' for x in range(config["start_year"],1+config["end_year"])]
  wb=load_workbook(filename = target,keep_vba=True)
  sheets=wb.sheetnames
  logger.info('{} existing sheets in {}'.format(len(sheets),target))
  if 'Sheet' in sheets:
    del wb['Sheet']
    logger.info('Removed Sheet')
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
        logger.info(f'Sheet {sheet_name} already exists, so not initializing')
        continue
      for table_info in sheet_info['tables']:
        
        
        # if new write the title and headings
        title_cell=f'{get_column_letter(first_not_hidden(table_info))}1'
        ws[title_cell].value=table_info['title']
        ws[title_cell].font=Font(name='Calibri',size=16,color='4472C4')
        col_defns=table_info['columns']
        col_count=len(col_defns)
        for col_no,col_data in enumerate(col_defns):
          ws.column_dimensions[get_column_letter(1+col_no)].width=col_data['width']
          if 'hidden' in sheet_info:
            ws.column_dimensions[get_column_letter(1+col_no)].hidden=col_data['name']in table_info['hidden']
          ws.cell(row=2,column=1+col_no,value=col_data['name'])
        if table_info['years']:
          for x, y in enumerate(year_columns):
            ws.column_dimensions[get_column_letter(1+x+col_count)].width=config['year_column_width']
            ws.cell(row=2,column=1+len(col_defns)+x,value=y)
          col_count+=len(year_columns)
        rng=f'A2:{get_column_letter(col_count)}3'
        tab = Table(displayName=table_info['name'], ref=rng)
        style = TableStyleInfo(name=sheet_group_info['table_style'],  showRowStripes=True)# Add a builtin style with striped rows and banded columns
        tab.tableStyleInfo = style
        ws.add_table(tab)
      ws.sheet_view.zoomScale=config['zoom_scale']
      
  wb.save(filename=target)
  logger.info('workbook {} saved'.format(target))

if __name__=='__main__':
    # execute only if run as a script
  parser = argparse.ArgumentParser(description ="set tabs the given workbook")
  parser.add_argument('target_file', help='provide the name of the output file')
  args=parser.parse_args()
  refresh_sheets(args.target_file)