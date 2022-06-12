#! /usr/bin/env python
import pandas as pd
import numpy as np
from utility import ws_for_table_name,df_for_range, get_val, put_val,df_for_table_name_for_update
from openpyxl.utils.cell import range_boundaries
from util.logs import get_logger

logger=get_logger(__file__)

def ira_distr_records():
  """Get the ira distribution records from Moneydance export
  
    Return a dataframe that has both inbound and outbound totals
  """

  filename="data/IRA-Distr.tsv"
  df=pd.read_csv(filename,sep='\t',skiprows=3) #,index_col=0)
  df.dropna(how="all",inplace=True)
  df=df[~df['Account'].str.contains("Total")] # remove totals
  df.fillna(0, inplace=True) # replace the NaN's with zeros
  cols=df.columns
  for col in cols[1:]:
    if col == 'Amount':
      df.loc[:,col]=df[col].str.replace(r'\$','',regex=True)
      df.loc[:,col]=df[col].str.replace(',','').astype(float)
    if col == 'Date':
      df[col] = pd.to_datetime(df[col])
  #remove the negatives, which are the transfers out of the IRA account
  #that way the totals will be the sum of the taxes and the postive amount transfered to the bank
  df=df[df.Amount>0]

  # create the year field to allow for pivot
  df["Year"]=df["Date"].dt.year
  df["Year"] = df["Year"].apply(lambda x: 'Y{}'.format(x))  
  return df

def main():
  """Adds the inbound and outbound transfers together and writes to spreadsheet"""
  
  df= ira_distr_records()

  summary= df.pivot_table(values='Amount',columns='Year',aggfunc='sum')
  
  source='data/fcast.xlsm'
  target = source
  
  # get the aux table and locate where to put the values
  aux_table,ws,ref,wb=df_for_table_name_for_update('tbl_aux')
  
  key='Income:I:Retirement income:IRA-Txbl-Distr'
  ix=aux_table.index.tolist().index(key) # the row in the table
  wix = ix +range_boundaries(ref)[1] + 1 # the row in the worksheet origin 1
  for col in summary.columns:
    val=summary.loc['Amount',col]
    cx = aux_table.columns.tolist().index(col)
    wcx = cx + range_boundaries(ref)[0] + 1 # the column index in the worksheet origin 1
    ws.cell(row=wix,column=wcx,value=val)

  wb.save(target)
  logger.info('saved to {}'.format(target))
  

if __name__ == "__main__":
  main()
