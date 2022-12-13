#!/usr/bin/env python
'''Tools for verifying the result of setup and hunting down problems'''
import pandas as pd
from dance.util.tables import df_for_table_name

def show_test(expected,found):
  '''compare expected and found for columns showing which items vary
  expected and found are of type pd.Series with a name.
  '''
  df=pd.DataFrame([expected,found]).T
  cols=df.columns
  print('\nComparison of '+' & '.join(cols))
  df['delta']=(df[cols[0]]-df[cols[1]]).round(2)
  sel= df.delta ==0
  print(df)
  print ('%d out of %d pass'%(sel.sum(),len(sel)))


def verify(workbook='data/test_wb.xlsm'):
  '''Various checks'''
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
  show_test(invest_income,invest_income_from_bal)

  # reinvestment - including banks since bank interest is accrued in place and not transfered in via add/Wdraw
  reinv_from_bal=balances.loc[balances.ValType=='Reinv Amt',y_cols].sum()
  reinv_from_bal.name='Sum of reinv amt on balances'
  reinv_removed=iande.loc['Expenses:Y:Invest:Reinv',y_cols]
  show_test(reinv_from_bal,reinv_removed)

  # HSA
  hsas=balances.loc[balances.AcctName.str.startswith('HSA'),'AcctName'].unique()
  for hsa in hsas:
    aw=balances.loc['Add/Wdraw'+hsa,y_cols]
    prs=iande.loc['Expenses:Y:Payroll Savings:'+hsa,y_cols]
    disb=iande.loc['Income:J:Distributions:HSA:'+hsa,y_cols]
    found=prs-disb
    found.name='P/R savings less distrib'
    show_test(aw,found)

  pass


if __name__=='__main__':
  print('''This requires that the workbook has been opened by Excel and saved.
  In order to populate the results of the Excel calculations.''')
  verify()
