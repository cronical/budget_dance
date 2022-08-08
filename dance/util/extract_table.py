#!/usr/bin/env python
'''Extract a table and save data as a json file
'''
import argparse
from dance.util.files import read_config
from dance.util.logs import get_logger
from dance.util.tables import df_for_table_name

logger=get_logger(__file__)

def extract(workbook,table,orient,out_file,data_only):
  df=df_for_table_name(table_name=table,workbook=workbook,data_only=data_only)
  if orient=='records':
    config=read_config() # locate the name of the index field
    for _,sheet_info in config['sheets'].items():
      for table_info in sheet_info['tables']:
        if not table_info['name']==table:
          continue
        column_info=table_info['columns']
        name = column_info[0]['name']
        df=df.reset_index().rename(columns={'index':name})
  df.to_json(out_file,orient=orient)
  logger.info(f'Wrote to {out_file}'.format())

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description ='Copies table from workbook and stores as a json output file')
  parser.add_argument('--workbook','-w',default='data/fcast.xlsm',help='Source workbook')
  parser.add_argument('--table', '-t',help='Source table name')
  parser.add_argument('--orient', '-o',default='index',choices=['index','records'],help='Use records if 1st fld not unique')
  parser.add_argument('--json', '-j',help='Name of the json file to store the output.')
  parser.add_argument('--data_only', '-d',action='store_true', default=False, help='To get data not formulas')

  args=parser.parse_args()
  extract(workbook=args.workbook,table=args.table,orient=args.orient,out_file=args.json,data_only=args.data_only)