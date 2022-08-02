#! /usr/bin/env python
'''For actual years, loads the bank, credit card and non-bank transfers into the 'transfers_actl' tab

This handles creating nested account keys, groups and totals as well as the raw data.

'''

import pandas as pd
import numpy as np

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

from bank_actl_load import bank_cc_changes
from dance.util.books import fresh_sheet
from dance.util.files import  tsv_to_df

def non_bank_transfers():
  '''get the in and out flows for the non bank transfers, prepare the keys and return a dataframe'''

  df=tsv_to_df ('data/transfers.tsv',skiprows=3)

  df=df[~df['Account'].isnull()] #remove the blank rows
  df=df[~df['Account'].str.contains('TRANSFERS')] # remove the headings and totals

  # throw away total column
  df.rename(columns={'Total':'level'},inplace=True)

  # create the key field to allow for pivot
  # fill it first with a temporary value used to compute the heirarchy level
  df.insert(loc=0,column='key',value=df.Account.str.lstrip())
  #create a level indicator as a dataframe field, then as a list
  df['level']=((df.Account.str.len() - df.key.str.len())-4)/3
  level=[int(x) for x in df.level.tolist()]
  del df['level']

  keys=[]
  keyparts=df.Account.tolist()
  rows=list(range(0,len(level))) # rows and columns are origin 0, excel uses origin 1 plus it contains the headings so for rows its off by 2
  last_level=-1
  for rw in rows:
    lev=level[rw]
    if 0==lev:
      pathparts=[]
    else:
      if lev > last_level: pathparts.append(keyparts[rw-1].strip())
      if lev < last_level:
        pathparts=pathparts[:-1]
    a=pathparts.copy()
    a.append(keyparts[rw].strip())
    keys.append(':'.join(a))
    last_level=lev

  # put the keys into the df and make that the index
  df['key']=keys
  df.set_index('key',inplace=True)

  # change the year columns to Y+year format
  for cn in df.columns.values.tolist():
    try:
      n=int(cn)
      nn = 'Y{}'.format(n)
      df.rename(columns={cn:nn},inplace=True)
    except ValueError:
      n=0

  return df

def process():
  '''loads the transfers into the 'transfers_actl' tab'''
  df=non_bank_transfers()

  # bring in the bank data
  bank_changes=bank_cc_changes()

  #combine the sets
  df =pd.concat([df,bank_changes])

  #the parent accounts don't contain data.  Get a list of those
  parents=[]
  for _,row in df.iterrows():
    if not ':' in row.Account:
      if all([0==x for x in row.to_list()[1:]]):
        parents.append(row.Account.strip())

  # summary adds the inbound and outbound transfers together
  summary=pd.pivot_table(df,index=['key'],values=df.columns[1:],aggfunc=np.sum)

  #prepare target file
  source='data/fcast.xlsm'
  target = source
  sheet= 'transfers_actl'
  tab_tgt='tbl_transfers_actl'

  wb = load_workbook(filename = source, read_only=False, keep_vba=True)

  wb=fresh_sheet(wb,sheet)
  ws = wb[sheet]

  #copy the data in to file and make adjustments to the file
  cols=list(range(0,summary.shape[1]))
  # set up the columns
  ws.cell(1,1,value='Account')
  for cl in cols:
    val=summary.columns[cl]
    ws.cell(1,cl+2,value=val)
  groups=[] # level, start, end
  #keep track of nesting of accounts
  heir=[]
  stot=[]
  rw=0 # add 2 for row is in excel
  xl_off=2
  keys=summary.index
  level=[x.count(':')for x in keys.tolist()]
  next_level=level[1:]+[0]
  for ky in keys:
    # if they key or any of its parts an exact match to one of the parents then we defer writing it
    if all([x in parents for x in ky.split(':')]) :
      heir.append(ky)# the key and the subtotal count
      stot.append(0)
    else:
      #determine how far back to look for the subtotal
      pending=len(heir)
      xl_row=rw+xl_off-pending

      #write the values from this row
      data_row=summary.loc[ky]
      ws.cell(xl_row,1,value=ky)
      for cl in cols:
        ws.cell(xl_row,cl+2,value=-data_row[cl])

      #process subtotals if there are any
      if pending>0:
        stot[-1]=stot[-1]+1 # include the row we just wrote in the subtotal

        # if the next row is at a lower level, then insert a total row for each time it pops
        pop_count=level[rw]-next_level[rw]
        adj_row=0
        while pop_count>0:
          nr_items_to_st=stot[-1]

          # subtotal row location adds one for each pop
          adj_row=adj_row+1
          stot_row=xl_row+adj_row

          # locate the start of the items to subtotal
          xl_start_row= stot_row - nr_items_to_st

          # insert the label and the formulas
          ws.cell(stot_row,1,value=heir[-1] + ' - TOTAL')
          for cl in cols:
            let=get_column_letter(cl+2)
            formula='=subtotal(9,{}{}:{}{})'.format(let,xl_start_row,let,stot_row-1)
            ws.cell(stot_row,cl+2,value=formula)

          # capture the grouping info
          groups.append([level[rw]-(adj_row-1),xl_start_row,stot_row-1])

          # pop the items
          heir.pop()
          stot.pop()
          pop_count=pop_count-1

          # include the count in the next higher level
          if len(stot)>0:
            stot[-1]=stot[-1]+nr_items_to_st+1
    rw=rw+1


  # set the label column width
  ws.column_dimensions['A'].width = 45

  # run through all rows and format numbers
  rows=list(range(0,rw))
  for rw in rows:
    #for all cells apply formats
    for cl in cols:
      ws.cell(column=cl+2,row=rw+2).number_format='#,###,##0;-#,###,##0;'-''

  # sort the row groups definitions: highest level to lowest level
  def getlev (e):
    return e[0]

  # use a histogram to determine where each group's foot print overlaps with the span of other groups
  hist=[0]*max([rw]+[x[2]for x in groups]) # handle case when last row is still indented
  groups.sort(key=getlev)
  for grp in groups:
    foot=list(range(grp[1]-1,grp[2]))
    mx=1+max([hist[x]for x in foot])
    grp[0]=mx
    for x in foot:
      hist[x]=hist[x]+1

  groups.sort(key=getlev)

  for grp in groups:
    ws.row_dimensions.group(start=grp[1],end=grp[2],outline_level=grp[0])



  # make this into a table
  rng=ws.dimensions
  tab = Table(displayName=tab_tgt, ref=rng)

  # Add a builtin style with striped rows and banded columns
  # The styles are seen on the table tab in excel broken into Light, Medium and Dark.
  # The number seems to be the index in that list (top to bottom, left to right, origin 1)
  style = TableStyleInfo(name='TableStyleMedium7',  showRowStripes=True)
  tab.tableStyleInfo = style

  ws.add_table(tab)

  wb.save(target)

if __name__ == '__main__':
  process()
