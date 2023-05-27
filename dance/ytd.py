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
  defaults={'workbook':'data/test_wb.xlsm','storage':'./data/ytd_data.json'}# TODO fcast
  parser = argparse.ArgumentParser(description ='Copies data from ytd tab to file or from file to ytd tab and iande.')
  parser.add_argument('-s','--save',help='saves data from the current tab to the file',action='store_true')
  parser.add_argument('-l','--load',help='loads the file data to the current tab',action='store_true')
  parser.add_argument('-f','--forward',help='carries the projected values to the first forecast year in the iande table'
                      ,action='store_true')
  parser.add_argument('-w','--workbook',default=defaults['workbook'],help='Target workbook. Default='+defaults['workbook'])
  parser.add_argument('-p','--path',default=defaults['storage'] ,help='The path and name of the storage file. Default='+defaults['storage'])
  args=parser.parse_args()
  config=read_config()
  ffy=config['first_forecast_year']
  if args.save:
    df= df_for_table_name('tbl_current',args.workbook,data_only=True)# key is in index
    ytd_fld_ix=list(df.columns.str.startswith('Y')).index(True)
    ytd_fld=df.columns[ytd_fld_ix]
    key_val=df.loc[(df.is_leaf==1) & (df.Factor.notna() | df.Add.notna()),[ytd_fld,'Factor','Add','Year']]
    key_val=key_val.fillna(0) 
    with open (args.path,'w',encoding='utf-8') as f:
      data=json.loads(key_val.to_json(orient='index'))
      json.dump(data,f,ensure_ascii=False,indent=2)
    logger.info('Wrote %d items to %s'%(len(key_val),args.path))
  if args.load or args.forward:
    wb=load_workbook(filename = args.workbook,keep_vba=True)
    with open (args.path,encoding='utf-8')as f:
      df=pd.read_json(f,orient='index')

    row_offset=3 # 1 to change origin, 1 for title, 1 for heading
    col_offset=2 # 1 to change origin, 1 since key is in the index not a field

  tgt_year='Y%04d'%ffy
  for control in (
    {'select':args.load,'tab':'current','sources':['Factor','Add'],'targets':['Factor','Add']},
    {'select':args.forward,'tab':'iande','sources':['Year'],'targets':[tgt_year]}
    ):
    src_tgt=list(zip(control['sources'],control['targets']))
    if control['select']:
      tab=control['tab']
      ws=wb[tab]
      tgt_df=df_for_table_name('tbl_'+tab,args.workbook,data_only=True)
      idx = tgt_df.index.to_list() # key is in index
      for ix,values in df.iterrows():
        for src,tgt in src_tgt:
          cx=col_offset+tgt_df.columns.to_list().index(tgt)
          rx=row_offset+idx.index(ix)
          val=values[src]
          ws.cell(row=rx,column=cx).value=val
        if tab=='current':
          # recompute reprojected year, in case the excel calc has not yet run.
          yx=col_offset+list(tgt_df.columns.str.startswith('Y')).index(True) # locate the ytd date column in the latest tsv
          df.at[ix,'Year']=ws.cell(row=rx,column=yx).value*values['Factor']+values['Add'] 
      wb.save(args.workbook)
      logger.info('Wrote %d %s values into table tbl_%s'%(df.shape[0],', '.join(control['targets']),control['tab']))
