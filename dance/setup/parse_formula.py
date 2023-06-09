'''experiment to parse filter formula to be used to determine number of rows in the result'''
import re
from openpyxl.formula import Tokenizer
cases=[
    '=FILTER(tbl_accounts[Account],tbl_accounts[Active])',
    '=SORT(FILTER(tbl_accounts[Account],tbl_accounts[Active]))',
    '=FILTER(tbl_accounts[Account],tbl_accounts[Active]=1)',
    '=FILTER(tbl_accounts[Account],(tbl_accounts[Active]=1))',
    '=FILTER(tbl_accounts[Account],(tbl_accounts[Active]=1)*(tbl_accounts[No distr plan]=1))',
    '=FILTER(tbl_accounts[Account],tbl_accounts[Active]*tbl_accounts[No distr plan])',
    '=FILTER(tbl_accounts[Account],(tbl_accounts[Type]="I")+(tbl_accounts[Type]="B"))'
]
for formula in cases:
  pat=re.compile('tbl_[a-zA-Z0-9]+')
  matches=pat.findall(formula)
  assert 1==len(set(matches)),'Formula does not refer to exactly one table'
  table_name=matches[0]
  print(formula)
  tok=Tokenizer(formula)
  print("\n".join("%12s%11s%9s" % (t.value, t.type, t.subtype) for t in tok.items))
  print("----\n")
  ix=formula.find('FILTER(')
  leading_parens=0
  for s in formula[0:ix]:
    leading_parens+= int(s==')')
  pass
pass