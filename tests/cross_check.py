#!/usr/bin/env python
'''Tools for verifying the result of spreadsheet creation and hunting down problems

  This requires that the workbook has been opened by Excel and saved.
  In order to populate the results of the Excel calculations.'''
import argparse
import json
import sys
import textwrap

import pandas as pd

from dance.util.files import read_config
from dance.util.logs import get_logger
from dance.util.tables import df_for_table_name
from tests.balance_check import balance_test_pairs
from tests.iande_check import iande_test_pairs
from tests.helpers import get_row_set

config=read_config()
logger=get_logger(__file__)

class Tester:
  '''Does the comparisons and keeps track of counts'''
  def __init__(self):
    self.test_count=0
    self.stats={} # keys are the test group, values are two element lists: element count, success count
  def __str__(self):
    return f'a tester. {self.test_count} tests run'
  def get_stats(self):
    '''Get a dictionary of stats'''
    return self.stats

  def run_test(self,test_group,expected,found,tolerance=0.5,ignore_years=[],title='') ->list:
    '''under the heading of a test_group, compare expected and found for columns showing which items vary
    expected and found are of type pd.Series with a name.
    By default look for exact match, but if tolerance provided then the difference should be less than or equal to the tolerance.
    Returns a list of column names (years) where the test failed.
    '''
    if test_group in self.stats:
      group_stat=self.stats[test_group]
    else:
      group_stat=[0,0]
      self.stats[test_group]=group_stat
    df=pd.DataFrame([expected,found]).T
    ignore_msg=''
    if 0!=len(ignore_years):
      sel=[x not in ignore_years for x in df.index]
      df=df.loc[sel]
      ignore_msg=f' (IGNORING: {ignore_years})'
    cols=df.columns
    df['delta']=(df[cols[0]]-df[cols[1]]).round(2)
    zeros= df.delta.abs() <=tolerance
    short_cols=[textwrap.shorten(a,width=50,placeholder='...')for a in list(cols)]
    fmt=f'%d. {title}: ' + ' == '.join(short_cols)
    self.test_count += 1
    group_stat[0]+=len(zeros)
    group_stat[1]+=zeros.sum()
    msg=fmt % self.test_count 
    msg+=' --> %d out of %d pass'%(zeros.sum(),len(zeros))
    logger.info (msg+ignore_msg)
    failed=[]
    if zeros.sum()!=len(zeros):
      df=df.loc[~ zeros]
      df.columns=['Expected','Found','Difference']
      print(indent(df,"    "))
      failed=list(df.index)
    return failed

def heading(label,punc):
  '''show a heading'''
  n=(72-len(label))//2
  msg= ((punc*n)+' '+label+' ' + (punc*n))
  logger.info(msg)

def results(test_group,tester):
  '''returns 0 if all tests pass, otherwise 100*ratio of successes to test count'''
  punc='-'
  stats=tester.get_stats()
  if test_group=='*':
    test_group='All tests'
    punc='='
    count=success=0
    for tg in stats:
      c,s=stats[tg]
      count+=c
      success+=s
  else:
    count,success=stats[test_group]
  score=100*success/count
  msg=  test_group+ ': %d out of %d (%.2f %%)'%(success,count,score)
  n=(72-len(msg))//2
  msg= (punc*n)+' '+msg +' '+(punc*n)+'\n'
  logger.info(msg)
  score=int(score)
  if score==100:
    return 0
  return score

def legend(table_name,filter,agg=None):
  '''return a usable legend constructed from the table name and filter'''
  legend='_'.join(table_name.split('_')[1:])
  legend+='[%s]'%filter
  if agg is not None:
    legend += '.%s()'%agg
  return legend

def row_to_value(workbook,test_group,tester,table,row_name,row_values,tolerance=0,ignore=[],title=''):
  '''
    args: workbook
          test_group
          tester
          table: table name
          row_name: matches first column of table
          row_values: a list of values
          tolerance
          ignore - list of Yyears to ignore
  '''
  found=get_row_set(workbook,table,'index','index',in_list=[row_name]).squeeze()
  if found.shape[0]==0:
    raise ValueError("Nothing found in "+row_name)
  found.name=legend(table,row_name)
  idx=found.index
  # set all values as zero then fill them in.  this allows test set to not (yet) have the right length.
  expected=pd.Series(0*idx.shape[0],index=idx,name='expected')
  for x,v in enumerate(row_values):
    expected[x]=v
  expected.drop(labels=ignore,inplace=True)
  found.drop(labels=ignore,inplace=True)
  tester.run_test(test_group,expected,found,tolerance,title=title)

def row_to_row(workbook,test_group,tester,table_lines,factors=None,title=''):
  '''
  Helper to test that two single rows match OR
  if the filter gets more than one row, the sum of those rows (times the factor) is used.
  (the purpose of the factor is to allow for subtraction in the case of two lines)
  The lines are text to match on the index of each table.

    args: workbook
          test_group
          tester
          table_lines: a dict with table names as key and lines as values. 
          The first item in the dict is the expected value 
          The line may be a string - which will use a contains filter
          The line may be a list - which will use the in_list filter
          factor - a factor for each of expected and found. Its length should be the same as the number of rows to be selected.
  '''
  values=[]
  dfs=[] 
  tables=[]
  agg=None
  if factors is None:
    mult_by=[1,1]
  else:
    mult_by=factors.copy()

  for table,line in table_lines.items():
    factor=mult_by.pop(0)
    if isinstance(line,str):
      df=get_row_set(workbook,table,'index','index',contains=line)
    if isinstance(line,list):
      df=get_row_set(workbook,table,'index','index',in_list=line)

    tables.append(table)
    dfs.append(df)
    if df.shape[0] > 1:
      series=df.multiply(factor,axis=0).sum(axis=0)
      agg='sum'
    else:
      series=df.squeeze()
    series.name=legend(table,line,agg)
    values.append(series)
  failed=tester.run_test(test_group,values[0],values[1],title=title)
  if len(failed):
    spaces="    "
    print (f"{spaces}Addition info")
    print (f"{spaces}------ {tables[0]}")
    print (indent(dfs[0][failed],spaces))
    print (f"{spaces}------ {tables[1]}")
    print(indent(dfs[1][failed],spaces))
    pass

def indent(df,spaces):
  return spaces + df.to_string().replace("\n", "\n"+spaces)

def verify(workbook=None,test_group='*'):
  '''Various checks'''
  test_groups='iande,cross_check,balances,cash_flow,taxes'.split(',')
  if test_group!='*':
    test_groups=[test_group]

  tester=Tester()
  heading('TESTS','=')

  # =========================================
# I and E
  test_group="iande"
  if test_group in test_groups:
    heading(test_group,'-')

    # totals from export match
    df=iande_test_pairs(workbook)
    cols=df.columns
    tester.run_test(test_group,df[cols[0]],df[cols[1]],title="I(net of capgn sales), T, X match exported values")
    score=results(test_group=test_group,tester=tester)



  # =========================================

  test_group='cross_check'
  if test_group in test_groups:
    heading(test_group,'-')

# IRA distributions
    test_lines={
      'tbl_retir_vals':'IRA - ',
      'tbl_iande':'Income:J:Distributions:IRA - TOTAL'}
    row_to_row(workbook,test_group,tester,test_lines,title="IRA Distributions")
  
# Pensions
    test_lines={
      'tbl_retir_vals':'DB - ',
      'tbl_iande':'Income:I:Retirement income:Pension - TOTAL'}
    row_to_row(workbook,test_group,tester,test_lines,title="Pensions")

# bank interest
    test_lines={
      'tbl_balances':'Bank Accounts:Retain:Rlz Int/Gn',
      'tbl_iande': 'Income:I:Invest income:Int:Bank'
    }
    row_to_row(workbook,test_group,tester,test_lines,title="Bank interest")

    df=df_for_table_name(table_name='tbl_invest_actl',data_only=True,workbook=workbook)

# sheltered capgn-sales
    sel=(df.ValType=='Gains' ) & (df.Acct_txbl==0)
    keys=df.loc[sel].index.to_list()
    test_lines={
      'tbl_invest_actl': keys,
      'tbl_iande': 'Income:I:Invest income:CapGn:Shelt:Sales'
    }
    row_to_row(workbook,test_group,tester,test_lines,title="Non-txbl Gain from sales")
    
# non sheltered capgn - sales
    sel=(df.ValType=='Gains' ) & (df.Acct_txbl==1)
    keys=df.loc[sel].index.to_list()
    test_lines={
      'tbl_invest_actl': keys,
      'tbl_iande': 'Income:I:Invest income:CapGn:Sales'
    }

    row_to_row(workbook,test_group,tester,test_lines,title="Txbl gn from sales")

# cap gains
    test_lines={
    'tbl_iande':['Income:I:Invest income:CapGn:Sales','Income:I:Invest income:CapGn:Shelt:Sales'],
    'tbl_invest_actl':'Gains'}
    row_to_row(workbook,test_group,tester,test_lines,title="All Cap Gns from sales")

# txbl accounts invest income
    sel=(df.ValType=='Income' ) & (df.Acct_txbl==1)
    keys=df.loc[sel].index.to_list()
    test_lines={
      'tbl_invest_actl': keys,
      'tbl_iande': ['Income:I:Invest income:CapGn:Mut LT','Income:I:Invest income:CapGn:Mut ST','Income:I:Invest income:Div:Reg','Income:I:Invest income:Div:Tax-exempt',
                    'Income:I:Invest income:Int:Defered-tax','Income:I:Invest income:Int:Reg','Income:I:Invest income:Int:Tax-exempt','Income:I:Invest income:Int:Tax-exempt Muni Accrued Int Paid']
    }
    row_to_row(workbook,test_group,tester,test_lines,title="Txbl account invest income")
    pass

# Non-txbl invest income
    sel=(df.ValType=='Income' ) & (df.Acct_txbl==0)
    keys=df.loc[sel].index.to_list()
    test_lines={
      'tbl_invest_actl': keys,
      'tbl_iande': ['Income:I:Invest income:Int:Shelt','Income:I:Invest income:Div:Shelt','Income:I:Invest income:CapGn:Shelt:Distr']
    }
    row_to_row(workbook,test_group,tester,test_lines,title="Non-txbl invest income")
    pass

    # iande invest income tot matches rlz int/gn on balances
    test_lines={
      'tbl_iande':'Income:I:Invest income - TOTAL',
      'tbl_balances':'Rlz Int/Gn'}
    row_to_row(workbook,test_group,tester,test_lines,title="iande invest income tot matches rlz int/gn on balances")

# reinvestment - including banks since bank interest is accrued in place and not transfered in via add/Wdraw
    test_lines={
    'tbl_iande':'Expenses:Y:Invest:Reinv:Gross',
    'tbl_balances':'Retain - PRODUCT'}
    row_to_row(workbook,test_group,tester,test_lines,title="iande reinvest matches balances retained")

# HSA - compare add/wdraw balances with P/R savings less distrib
    aw=get_row_set(workbook,'tbl_balances','ValType','AcctName',in_list=['Add/Wdraw'])
    hsas=aw.loc[aw.index.str.startswith('HSA')].index.unique()
    for hsa in hsas:
      ignore=[]
      if 'Devenir' in hsa or 'GBD - Fidelity' in hsa:
        ignore=['Y2018']
      expected=aw.loc[hsa]
      table,filter,agg=('tbl_iande',hsa,'diff')
      hsa_rows=get_row_set(workbook,table,'index','index',contains=filter)
      # if there is an account move, there may be an extra row
      hsa_rows=hsa_rows.loc[~hsa_rows.index.str.contains('To Asst')]

      found=hsa_rows.diff(axis=0).tail(1).squeeze()
      found.name=legend(table,filter,agg)
      tester.run_test(test_group,expected,found,ignore_years=ignore,title=f"{hsa} - add/wdraw matches P/R savings less distrib")

    results(test_group=test_group,tester=tester)
  # ========================================

# Balances
  test_group='balances'
  if test_group in test_groups:
    heading(test_group,'-')

    # computed balances match exported balances
    df=balance_test_pairs(workbook)
    cols=df.columns
    tester.run_test(test_group,df[cols[0]],df[cols[1]],title="Computed balances match exported balances")
    score=results(test_group=test_group,tester=tester)
    # ========================================

# Cash flow
  test_group='cash_flow'
  if test_group in test_groups:
    heading(test_group,'-')
    # zero out
    table,line=('tbl_iande','TOTAL INCOME - EXPENSES')
    found=get_row_set(workbook,table,'index','index',contains=line).squeeze()
    found.name=legend(table,line)
    expected=found * 0
    expected[0]=-42.06
    expected[1]=42.06
    expected.name='expected'
    tester.run_test(test_group,expected,found,title="Cash flow")
 # ========================================

# Taxes 
  test_group='taxes'
  if test_group in test_groups:
    heading(test_group,'-')
    table='tbl_taxes'
    ignore=[]
    with open('data/known_test_values.json') as f:
      ktv=json.load(f)
    for key,values in ktv[table].items():
      if key.lower().startswith('ignore'):
        ignore=values
        logger.info(f'IGNORING: {ignore}')
        continue
      row_to_value(workbook=workbook,table=table,
      test_group=test_group,tester=tester,row_name=key,row_values=values,tolerance=1,ignore=ignore,
      title="Known value")

  # =========================================
  score=results(test_group='*',tester=tester)
  return score

if __name__=='__main__':
  # execute only if run as a script
  parser = argparse.ArgumentParser(description ='This program runs functional tests \
    by test group (or all).')
  parser.add_argument('-workbook',default=config['workbook'],help='provide an alternative workbook')
  parser.add_argument('-group',default='*',help='specify a single test group or * for all')
  args=parser.parse_args()
  score=verify(workbook=args.workbook,test_group=args.group)
  sys.exit(score)