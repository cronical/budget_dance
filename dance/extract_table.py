#!/usr/bin/env python
'''Extract a table and save data as a json file
'''
import argparse
import re
from dance.util.files import read_config
from dance.util.logs import get_logger
from dance.util.tables import df_for_table_name

config=read_config() 
logger=get_logger(__file__)

def count_leading_space(s): 
  match = re.search(r"^\s*", s) 
  return 0 if not match else match.end()

def extract(workbook,tables,data_only=None):
  '''Extract all tables in list'''
  logger.info("Source workbook is %s"%workbook)
  for table in tables: 
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

def eligible_tables():
  '''Returns list of all eligible tables'''
  eligible=[]
  for _,sheet_info in config['sheets'].items():
    for table_info in sheet_info['tables']:
      if 'data' in table_info:
        data_info=table_info['data']
        if 'type' not in data_info:
          continue
        source_data=data_info['type']
        orient=source_data.split('_')[-1]
        if orient not in ['records','index','template']:
          continue
        eligible.append(table_info['name'])   
  eligible.sort()
  return eligible

def main():
  default_wb=config['workbook']
  parser = argparse.ArgumentParser(description ='Copies table data from workbook and stores as a json or tsv output file.')
  parser.add_argument('--workbook','-w',default=default_wb,help=f'Source workbook. Default: {default_wb}')
  parser.add_argument('--data_only', '-d',action='store_true', default=False, help='To get data not formulas')
  me_grp=parser.add_mutually_exclusive_group(required=True)
  me_grp.add_argument('--table', '-t',help='Source table name, include tbl_')
  me_grp.add_argument('--all', '-a',action='store_true',help='Extract all eligible tables')
  me_grp.add_argument('--list', '-l',action='store_true',help='List all eligible tables')
  args=parser.parse_args()
  if args.all or args.list:
    tables=eligible_tables()
  else:
    tables=[args.table]
  if args.list:
    for table in tables:
      print (table)
  else:
    extract(workbook=args.workbook,tables=tables,data_only=args.data_only)

if __name__ == '__main__':
  main()