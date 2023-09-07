#!/usr/bin/env python
'''Extract a table and save data as a json file
'''
import argparse
from os import sep
from os.path import dirname
import re
from dance.util.files import read_config
from dance.util.logs import get_logger
from dance.util.tables import df_for_table_name

logger=get_logger(__file__)
def count_leading_space(s): 
  match = re.search(r"^\s*", s) 
  return 0 if not match else match.end()

def extract(workbook,table,out_file=None,data_only=None):
  logger.info("Source workbook is %s"%workbook)
  config=read_config() 
  # locate info such as orientation, the name of the index field
  column_info=None
  for _,sheet_info in config['sheets'].items():
    for table_info in sheet_info['tables']:
      if not table_info['name']==table:
        continue
      column_info=table_info['columns']
      data_info=table_info['data']
      if 'type' not in data_info:
         raise ValueError('No source_data type found for this table in config')
      source_data=data_info['type']
      orient=source_data.split('_')[-1]
      if orient not in ['records','index','template']:
         raise ValueError('This table is not sourced as json or template')
      if out_file is None: # default for the output file name
        out_file=data_info['path']
  if column_info is None:
    raise ValueError('Table not in config')
  if data_only is None:
    data_only=False
  df=df_for_table_name(table_name=table,workbook=workbook,data_only=data_only)
  if orient in['records','template']: # move index into column
    name = column_info[0]['name']
    df=df.reset_index().rename(columns={'index':name})
  if orient !='template':
    df.to_json(out_file,orient=orient)# ,date_format='iso'
  else:
    if 'template' not in data_info:
      raise ValueError('Table uses a template, but template not defined in config')
    template_info=data_info['template']
    indentation_note=''
    if 'fold_spacing' in template_info:
      # validate fold_spacing
      fold_spacing=template_info['fold_spacing']
      df['leading_spaces']=df.Line.apply(count_leading_space)
      sel=(df.leading_spaces%fold_spacing)==0
      if not sel.all():
        print('The following lines have leading spaces that are not multiples of %d'%fold_spacing)
        print(df.loc[(~sel),[template_info['fold_field'],'leading_spaces']])
        raise ValueError('Indents are damaged')
      del df['leading_spaces']
      indentation_note='Indentation must be %d spaces.'%fold_spacing
    with open(out_file,'w') as f:
      f.write('%s template\n'%('_'.join(table.split('_')[1:])).title())
      f.write('Template - styled as a Moneydance report saved as .tsv\n')
      f.write(indentation_note+'\n')
      df.to_csv(f,index=False,columns=template_info['fields'],sep='\t',date_format='%m/%d/%Y')
    
  logger.info(f'Wrote to {out_file}'.format())

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description ='Copies table data from workbook and stores as a json or tsv output file.')
  parser.add_argument('--workbook','-w',default='data/fcast.xlsm',help='Source workbook')
  parser.add_argument('--table', '-t',required=True,help='Source table name, include tbl_')
  parser.add_argument('--output', '-o',help='Name of the output file. Default is folder of workbook and configured data path')
  parser.add_argument('--data_only', '-d',action='store_true', default=False, help='To get data not formulas')

  args=parser.parse_args()
  extract(workbook=args.workbook,table=args.table,out_file=args.output,data_only=args.data_only)