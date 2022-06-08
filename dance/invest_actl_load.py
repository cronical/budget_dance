#! /usr/bin/env python
"""
Update the tab 'invest_actl'

Read data from 'data/xinvest.tsv' and performance reports 
merge and manipulate before writing to 'data/fcst.xlsm'

"""
import os
from dateutil.parser import parse
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

import pandas as pd
from utility import tsv_to_df,df_for_table_name
from utility import fresh_sheet
from util.logs import get_logger

logger=get_logger(__file__)
source='data/fcast.xlsm'
target = source
xfer_file="data/invest_x.tsv"
perf_file_prefix="invest-p-"
datadir='./data/'
sheet='invest_actl'
tab_tgt='tbl_invest_actl'
tab_style='TableStyleMedium7'
# The styles are seen on the table tab in excel broken into Light, Medium and Dark.
# The number seems to be the index in that list (top to bottom, left to right, origin 1)

logger.info("Starting investment actual load")

# get the account list
accounts=df_for_table_name('tbl_accounts')
accounts=accounts[accounts.Type == 'I']

# get the output of the Moneydance report
df=tsv_to_df (xfer_file,skiprows=3)
df.dropna(axis=0,how='any',inplace=True)
df=df[df["Account"].str.contains("TRANSFERS")==False]
df=df.groupby('Account').sum() # add the ins and outs
df=df.mul(-1)# fix the sign
df.index=df.index.str.strip() # remove leading spaces
df=df.loc[:,df.columns !='Total'] # drop the total column

# join these and keep only the data columns using the accounts list as the master
xfers=accounts.join(df)[df.columns.to_list()]
xfers.fillna(0, inplace=True) # replace the NaN's (where no transfers occurred) with zeros

files=os.listdir(datadir)
files.sort()
file_cnt=0
for file_name in files:
  if file_name.find(perf_file_prefix) == 0:
    #grab the year from the file name
    fn_year = file_name.split('.')[0].split('-')[-1]
    perf_file=datadir+file_name
    logger.info('Processing %s'%fn_year)
    # now work with the performance data for a year
    df=tsv_to_df (perf_file,skiprows=3)
    # first check to see if the year is valid and its a full year
    orig=[df.columns[x] for x in [1,5]]
    open_close=[parse(x)for x in orig]
    ys=[x.year for x in open_close]
    assert ys[0]==ys[1], "Report covers more than one year"
    assert (1+(open_close[1]-open_close[0]).days) in [365,366], "Not a full year"
    assert ys[0]==int(fn_year), "File name year does not equal internal year"
    # change to 'Open' and 'End'
    map={orig[0]:'Open',orig[1]:'End'}
    df.rename(columns=map,inplace=True)

    #get the rows in order
    df.loc[:,'Security']=df['Security'].fillna(value='')
    df=df.loc[df.Security.str.startswith('Total:')] # throw away the securities, just keep the accounts
    df=df.loc[df.Security != 'Total: '] # remove grand total
    df.loc[:,'Security']=df['Security'].str.replace('Total: ','') # just the account names

    # prepare for joins with common index 
    df.set_index('Security',inplace=True) 
    found=[x in accounts.index.to_list() for x in df.index.to_list()]
    if not all(found):

      print("Not all accounts for %s are in master. Missing:"%fn_year)
      for a in [x for x in df.index.to_list() if x not in accounts.index.to_list()]:
        print('  %s'%a)
      assert all(found)

    # all master accts, and all performance columns
    df=accounts.join(df)[df.columns] 
    df.fillna(value=0,inplace=True) # zero out the perf values for accts in master not perf
    
    # append the transfers
    df=df.join(xfers[fn_year])
    df.rename(columns={fn_year:'Transfers'},inplace=True)

    # compute the two gain fields 
    df=df.assign(Realized=lambda x: x.Income + x.Gains) # compute the realized gains
    df=df.assign(Unrealized=lambda x: x.End - (x.Open+x.Transfers+x.Realized))
    
    # use names in spreadsheet 
    map={'Transfers':'Add/Wdraw','Realized':'Rlz Int/Gn','Unrealized':'Unrlz Gn/Ls'} 
    df.rename(columns=map,inplace=True)

    # rework so the rows of 3 value types for each account
    rows=df[['Add/Wdraw','Rlz Int/Gn','Unrlz Gn/Ls']].transpose().stack().reset_index()
    map=dict(zip(rows.columns.to_list(),['ValType','AcctName','Y'+fn_year]))
    rows.rename(columns=map,inplace=True)
    rows=rows.assign(Key=lambda x: x.ValType + x.AcctName)
    rows.set_index('Key',inplace=True)
    if file_cnt==0:
      table=rows
    else:
      table=table.join(rows[rows.columns.to_list()[-1]])
    file_cnt=file_cnt+1

# put the data into the spreadsheet
table.reset_index(inplace=True) # puts the key back into 1st column
wb = load_workbook(filename = source, read_only=False, keep_vba=True)
logger.info('Loaded workbook from {}'.format(source))
wb=fresh_sheet(wb,sheet)
ws=wb[sheet]
cols=list(range(0,table.shape[1]))
# for set heading values for columns
for cl in list(range(0,table.shape[1])):
  ws.cell(1,cl+1,value=table.columns[cl])
# the data items 
for rw in list(range(0,table.shape[0])):
  for cl in cols:
    val=table.loc[table.index[rw]][cl]
    ws.cell(rw+2,cl+1,value=val)

# set the column widths
w=[35, 20, 25] +[15]*(table.shape[1]-3)
for i in list(range(0,len(w))):
  ws.column_dimensions[get_column_letter(1+i)].width=w[i]

# make the range a table in Excel  
rng=ws.dimensions
tab = Table(displayName=tab_tgt, ref=rng)

# Add a builtin style with striped rows and banded columns
style = TableStyleInfo(name=tab_style,  showRowStripes=True)
tab.tableStyleInfo = style
ws.add_table(tab)
logger.info('Table {} added'.format(tab_tgt))

wb.save(target)
logger.info('Saved to {}'.format(target))

