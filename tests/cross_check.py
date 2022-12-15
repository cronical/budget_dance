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

def verify(workbook='data/test_wb.xlsm'):
  '''Various checks'''
  tester=Tester()
  test_group='cross-check'
  heading('TESTS','=')
  heading(test_group,'-')

  # expenses X and T on iande match iande_actl
  lines= ['Expenses:X - TOTAL','Expenses:T - TOTAL']
  for line in lines:
    table,filter,agg=('tbl_iande_actl',line,None)
    expected=get_row_set(workbook,'tbl_iande_actl','index','index',contains=filter).squeeze()
    expected.name=legend(table,filter,agg)
    table,filter,agg=('tbl_iande',line,None)
    found=get_row_set(workbook,table,'index','index',in_list=[filter]).squeeze()
    found.name=legend(table,filter,agg)
    tester.run_test(test_group,expected,found)


  # investment gains on i and e match rlz int/gn on balances
  expected=get_row_set(workbook,'tbl_iande','index','index',contains='Income:I:Invest income - TOTAL').squeeze()
  table,filter,agg=('tbl_balances','Rlz Int/Gn','sum')
  found=get_row_set(workbook,table,'ValType','AcctName',in_list=[filter]).sum()
  found.name=legend(table,filter,agg)
  tester.run_test(test_group,expected,found)

  # reinvestment - including banks since bank interest is accrued in place and not transfered in via add/Wdraw
  expected=get_row_set(workbook,'tbl_iande','index','index',contains='Expenses:Y:Invest:Reinv').squeeze()
  table,filter,agg=('tbl_balances','Reinv Amt','sum')
  found=get_row_set(workbook,table,'ValType','AcctName',in_list=[filter]).sum()
  found.name=legend(table,filter,agg)
  tester.run_test(test_group,expected,found)

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

  test_group='balances'
  heading(test_group,'-')

  df=balance_test_pairs('data/test_wb.xlsm')
  cols=df.columns
  tester.run_test(test_group,df[cols[0]],df[cols[1]])
  results(test_group=test_group,tester=tester)

  results(test_group='*',tester=tester)

if __name__=='__main__':

  verify()
