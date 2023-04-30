#! /usr/bin/env python
'''Save or load YTD values'''
import argparse
import json
from openpyxl import load_workbook
import pandas as pd
from dance.util.files import read_config
from dance.util.logs import get_logger
from dance.util.tables import df_for_table_name
logger=get_logger(__file__)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description ='Copies data from ytd tab to file or from file to ytd tab and iande.')
  parser.add_argument('-s','--save',help='saves data from the current tab to the file',action='store_true')
  parser.add_argument('-l','--load',help='loads the file data to the current tab',action='store_true')
  parser.add_argument('-f','--forward',help='carries the projected values to the first forecast year in the iande table'
                      ,action='store_true')
  parser.add_argument('--workbook','-w',default='data/test_wb.xlsm',help='Target workbook')# TODO fcast
  parser.add_argument('--path','-p',default= './data/ytd_data.json',help='The path and name of the storage file')
  args=parser.parse_args()
  logger.info(args)
  config=read_config()
  ffy=config['first_forecast_year']
  if args.save:
    df= df_for_table_name('tbl_current',args.workbook,data_only=True)# key is in index
    ytd_fld_ix=list(df.columns.str.startswith('Y')).index(True)
    ytd_fld=df.columns[ytd_fld_ix]
    key_val=df.loc[(df.is_leaf==1) & df.Factor.notna(),[ytd_fld,'Factor','Year']]
    with open (args.path,'w',encoding='utf-8') as f:
      json.dump(key_val.to_json(),f,ensure_ascii=False,indent=2)
    logger.info('Wrote %d items to %s'%(len(key_val),args.path))
  if args.load or args.forward:
    wb=load_workbook(filename = args.workbook,keep_vba=True)
    with open (args.path,encoding='utf-8')as f:
      df=pd.read_json(json.load(f),orient='index').T
    ytd_fld=df.columns[0]
    df['Year']=df[ytd_fld]*df['Factor'] # recompute reprojected year, in case the excel calc has not yet run.
    row_offset=3 # 1 to change origin, 1 for title, 1 for heading
    col_offset=2 # 1 to change origin, 1 since key is in the index not a field
  for control in (
    {'select':args.load,'tab':'current','field':'Factor','target':'Factor'},
    {'select':args.forward,'tab':'iande','field':'Year','target':'Y%04d'%ffy}
    ):
    if control['select']:
      ws=wb[control['tab']]
      tgt_df=df_for_table_name('tbl_'+control['tab'],args.workbook,data_only=True)
      cx=tgt_df.columns.to_list().index(control['target'])
      idx = tgt_df.index.to_list() # key is in index
      for ix,values in df.iterrows():
        ws.cell(row=row_offset+idx.index(ix),column=col_offset+cx).value=values[control['field']]
      wb.save(args.workbook)
      logger.info('Wrote %d %s values into %s table'%(df.shape[0],control['target'],control['tab']))
