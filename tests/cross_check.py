#!/usr/bin/env python
'''Tools for verifying the result of setup and hunting down problems

  This requires that the workbook has been opened by Excel and saved.
  In order to populate the results of the Excel calculations.'''
import argparse
import json
import pandas as pd

from tests.balance_check import balance_test_pairs
from tests.helpers import get_row_set

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

  def run_test(self,test_group,expected,found,tolerance=0.5):
    '''under the heading of a test_group, compare expected and found for columns showing which items vary
    expected and found are of type pd.Series with a name.
    By default look for exact match, but if tolerance provided then the difference should be less than or equal to the tolerance.
    '''
    if test_group in self.stats:
      group_stat=self.stats[test_group]
    else:
      group_stat=[0,0]
      self.stats[test_group]=group_stat
    df=pd.DataFrame([expected,found]).T
    cols=df.columns
    df['delta']=(df[cols[0]]-df[cols[1]]).round(2)
    zeros= df.delta.abs() <=tolerance
    msg='%d '+' == '.join(cols)
    self.test_count += 1
    group_stat[0]+=len(zeros)
    group_stat[1]+=zeros.sum()
    msg=msg % self.test_count 
    msg+=' --> %d out of %d pass'%(zeros.sum(),len(zeros))
    print (msg)
    if zeros.sum()!=len(zeros):
      df=df.loc[~ zeros]
      df.columns=['Expected','Found','Difference']
      df.index=df.index.str.replace('Y','...Y')
      print(df)
      print('')


def heading(label,punc):
  '''print a heading'''
  n=(72-len(label))//2
  msg= ((punc*n)+' '+label+' ' + (punc*n))
  print(msg)

def results(test_group,tester):
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
  msg=  test_group+ ': %d out of %d (%.2f %%)'%(success,count,100*success/count)
  n=(72-len(msg))//2
  msg= (punc*n)+' '+msg +' '+(punc*n)+'\n'
  print(msg)

def legend(table_name,filter,agg=None):
  '''return a usable legend constructed from the table name and filter'''
  legend='_'.join(table_name.split('_')[1:])
  legend+='[%s]'%filter
  if agg is not None:
    legend += '.%s()'%agg
  return legend

def row_to_value(workbook,test_group,tester,table,row_name,row_values,tolerance=0):
  '''
    args: workbook
          test_group
          tester
          table: table name
          row_name: matches first column of table
          row_values: a list of values
          tolerance
  '''
  found=get_row_set(workbook,table,'index','index',in_list=[row_name]).squeeze()
  found.name=legend(table,row_name)
  idx=found.index
  # set all values as zero then fill them in.  this allows test set to not (yet) have the right length.
  expected=pd.Series(0*idx.shape[0],index=idx,name='expected')
  for x,v in enumerate(row_values):
    expected[x]=v
  tester.run_test(test_group,expected,found,tolerance)

def row_to_row(workbook,test_group,tester,table_lines):
  '''
  Helper to test that two single rows match OR
  if the filter gets more than one row, the sum of those rows is used.
  The lines are text to match on the index of each table.

    args: workbook
          test_group
          tester
          table_lines: a dict with table names as key and lines as values. 
          The first item in the dict is the expected value 
          The line may be a string - which will use a contains filter
          The line may be a list - which will use the in_list filter
  '''
  values=[]
  agg=None
  for table,line in table_lines.items():
    if isinstance(line,str):
      df=get_row_set(workbook,table,'index','index',contains=line)
    if isinstance(line,list):
      df=get_row_set(workbook,table,'index','index',in_list=line)
    if df.shape[0] > 1:
      series=df.sum(axis=0)
      agg='sum'
    else:
      series=df.squeeze()
    series.name=legend(table,line,agg)
    values.append(series)
  tester.run_test(test_group,values[0],values[1])

def verify(workbook='data/test_wb.xlsm',test_group='*'):
  '''Various checks'''
  test_groups='cross_check,balances,cash_flow,taxes'.split(',')
  if test_group!='*':
    test_groups=[test_group]

  tester=Tester()
  heading('TESTS','=')

  # =========================================
  test_group='cross_check'
  if test_group in test_groups:
    heading(test_group,'-')

    # Income, expenses totals on iande match iande_actl
    lines= ['Income:I - TOTAL','Expenses:X - TOTAL','Expenses:T - TOTAL']
    for line in lines:
      row_to_row(workbook,test_group,tester,{'tbl_iande_actl':line,'tbl_iande':line})

    # cap gains
    test_lines={
    'tbl_iande':['Income:I:Invest income:CapGn:Sales','Income:I:Invest income:CapGn:Shelt:Sales'],
    'tbl_invest_actl':'Gains'}
    row_to_row(workbook,test_group,tester,test_lines)

    # IRA distributions
    test_lines={
      'tbl_retir_vals':'IRA - ',
      'tbl_iande':'Income:J:Distributions:IRA - TOTAL'}
    row_to_row(workbook,test_group,tester,test_lines)
  
    # Pensions
    test_lines={
      'tbl_retir_vals':'DB - ',
      'tbl_iande':'Income:I:Retirement income:Pension - TOTAL'}
    row_to_row(workbook,test_group,tester,test_lines)

    # investment gains on i and e match rlz int/gn on balances
    test_lines={
      'tbl_iande':'Income:I:Invest income - TOTAL',
      'tbl_balances':'Rlz Int/Gn'}
    row_to_row(workbook,test_group,tester,test_lines)

  # reinvestment - including banks since bank interest is accrued in place and not transfered in via add/Wdraw
    test_lines={
    'tbl_iande':'Expenses:Y:Invest:Reinv',
    'tbl_balances':'Reinv Amt'}
    row_to_row(workbook,test_group,tester,test_lines)

    # HSA - compare add/wdraw balances with P/R savings less distrib
    aw=get_row_set(workbook,'tbl_balances','ValType','AcctName',in_list=['Add/Wdraw'])
    hsas=aw.loc[aw.index.str.startswith('HSA')].index.unique()
    for hsa in hsas:
      expected=aw.loc[hsa]
      table,filter,agg=('tbl_iande',hsa,'diff')
      found=get_row_set(workbook,table,'index','index',contains=filter).diff(axis=0).tail(1).squeeze()
      found.name=legend(table,filter,agg)
      tester.run_test(test_group,expected,found)

    results(test_group=test_group,tester=tester)
  # ========================================

  test_group='balances'
  if test_group in test_groups:
    heading(test_group,'-')

    # computed balances match exported balances
    df=balance_test_pairs('data/test_wb.xlsm')
    cols=df.columns
    tester.run_test(test_group,df[cols[0]],df[cols[1]])
    results(test_group=test_group,tester=tester)
    # ========================================
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
    tester.run_test(test_group,expected,found)
 # ========================================
  test_group='taxes'
  if test_group in test_groups:
    heading(test_group,'-')
    table='tbl_taxes'
    with open('data/known_test_values.json') as f:
      ktv=json.load(f)
    for key,values in ktv[table].items():
      row_to_value(workbook=workbook,table=table,
      test_group=test_group,tester=tester,row_name=key,row_values=values,tolerance=1)

  # =========================================
  results(test_group='*',tester=tester)


if __name__=='__main__':
  # execute only if run as a script
  parser = argparse.ArgumentParser(description ='This program runs functional tests \
    by test group (or all).')
  parser.add_argument('-workbook',default='data/test_wb.xlsm',help='provide an alternative workbook')
  parser.add_argument('-group',default='*',help='specify a single test group or * for all')
  args=parser.parse_args()
  verify(workbook=args.workbook,test_group=args.group)
