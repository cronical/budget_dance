#!/usr/bin/env python
'''Tools for verifying the result of setup and hunting down problems

  This requires that the workbook has been opened by Excel and saved.
  In order to populate the results of the Excel calculations.'''
import pandas as pd
from dance.util.tables import df_for_table_name
from tests.balance_check import balance_test_pairs

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
  count,success=tester.get_stats()[test_group]
  msg=  test_group+ ': %d out of %d (%.2f %%)'%(success,count,100*success/count)
  n=(72-len(msg))//2
  msg= (punc*n)+' '+msg +' '+(punc*n)+'\n'
  print(msg)


def verify(workbook='data/test_wb.xlsm'):
  '''Various checks'''
  tester=Tester()
  test_group='cross-check'
  heading('TESTS','=')
  heading(test_group,'-')
  iande_actl=df_for_table_name('tbl_iande_actl',workbook=workbook,data_only=True)
  cols=iande_actl.columns
  y_cols=cols.drop('Account')
  iande=df_for_table_name('tbl_iande',workbook=workbook,data_only=True)[cols].fillna(0).round(2)
  balances=df_for_table_name('tbl_balances',workbook=workbook,data_only=True)
  bal_cols=balances.columns[:3].append(y_cols)
  balances=balances[bal_cols].round(2) # avoid scientific notation

  invest_income=iande.loc['Income:I:Invest income - TOTAL',y_cols]
  invest_income_from_bal=balances.loc[balances.ValType=='Rlz Int/Gn',y_cols].sum()
  invest_income_from_bal.name='Sum of Rlz Int/Gn from balances'
  tester.run_test(test_group,invest_income,invest_income_from_bal)

  # reinvestment - including banks since bank interest is accrued in place and not transfered in via add/Wdraw
  reinv_from_bal=balances.loc[balances.ValType=='Reinv Amt',y_cols].sum()
  reinv_from_bal.name='Sum of reinv amt on balances'
  reinv_removed=iande.loc['Expenses:Y:Invest:Reinv',y_cols]
  tester.run_test(test_group,reinv_from_bal,reinv_removed)

  # HSA
  hsas=balances.loc[balances.AcctName.str.startswith('HSA'),'AcctName'].unique()
  for hsa in hsas:
    aw=balances.loc['Add/Wdraw'+hsa,y_cols]
    prs=iande.loc['Expenses:Y:Payroll Savings:'+hsa,y_cols]
    disb=iande.loc['Income:J:Distributions:HSA:'+hsa,y_cols]
    found=prs-disb
    found.name='P/R savings less distrib'
    tester.run_test(test_group,aw,found)

  results(test_group=test_group,tester=tester)

  test_group='balances'
  heading(test_group,'-')

  df=balance_test_pairs('data/test_wb.xlsm')
  cols=df.columns
  tester.run_test(test_group,df[cols[0]],df[cols[1]])
  results(test_group=test_group,tester=tester)

  heading('END TESTS','=')


if __name__=='__main__':

  verify()
