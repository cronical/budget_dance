#!/usr/bin/env python
'''Tools for verifying the result of setup and hunting down problems

  This requires that the workbook has been opened by Excel and saved.
  In order to populate the results of the Excel calculations.'''
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

  def run_test(self,test_group,expected,found):
    '''under the heading of a test_group, compare expected and found for columns showing which items vary
    expected and found are of type pd.Series with a name.
    '''
    if test_group in self.stats:
      group_stat=self.stats[test_group]
    else:
      group_stat=[0,0]
      self.stats[test_group]=group_stat
    df=pd.DataFrame([expected,found]).T
    cols=df.columns
    df['delta']=(df[cols[0]]-df[cols[1]]).round(2)
    zeros= df.delta ==0
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

def verify(workbook='data/test_wb.xlsm'):
  '''Various checks'''
  tester=Tester()
  test_group='cross-check'
  heading('TESTS','=')
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
  heading(test_group,'-')

  # computed balances match exported balances
  df=balance_test_pairs('data/test_wb.xlsm')
  cols=df.columns
  tester.run_test(test_group,df[cols[0]],df[cols[1]])
  results(test_group=test_group,tester=tester)
  # ========================================
  test_group='cash flow'
  heading(test_group,'-')

  # zero out
  table,line=('tbl_iande','TOTAL INCOME - EXPENSES')
  found=get_row_set(workbook,table,'index','index',contains=line).squeeze()
  found.name=legend(table,line)
  zeros=found * 0
  zeros.name='zeros'
  tester.run_test(test_group,zeros,found)
  # =========================================
  results(test_group='*',tester=tester)


if __name__=='__main__':

  verify()
