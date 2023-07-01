'''tests formula handling'''
import pandas as pd
from dance.util.xl_formulas import table_ref
from dance.util.row_tree import multi_agg_subtotals, collapse_adjacent,address_phrase

import pytest # pylint: disable=unused-import

def test_single_match():
  test='=get_val("End Bal" &  [@AcctName],"tbl_balances",y_offset(this_col_name(),-1))'
  expected='=get_val("End Bal" &  [[#This Row],[AcctName]],"tbl_balances",y_offset(this_col_name(),-1))'
  assert expected == table_ref(test)

def test_no_match():
  test='quick red fox etc'
  assert test == table_ref(test)

def test_spaces_in_name():
  test='something [@with a name] having spaces'
  expected='something [[#This Row],[with a name]] having spaces'
  assert expected == table_ref(test)

def test_multiple_different():
  test='[@AcctName],[@Type],[@Active]'
  expected='[[#This Row],[AcctName]],[[#This Row],[Type]],[[#This Row],[Active]]'
  assert expected == table_ref(test)

def test_multi_agg_subtotals():
  line='z,__a,____b,____c,__a_-_min,__d,____e,______f,______g,____e_-_product,____h,__d_-_total,i,j,z_-total'.split(',')
  df=pd.DataFrame(line)
  df['level']= [0,1,2,2,1,1,2,3,3,2,2,1,1,1,0]
  print (df)
 
  groups=[[0,0,14],[1,1,4],[1,5,11],[2,6,9]]
  rows=multi_agg_subtotals(groups)
  assert rows[0]==[4,11,12,13]
  assert rows[1]== [2,3]
  assert rows[2]== [9,10]
  assert rows[3]== [7,8]

def test_collapse_adjacent():
  assert collapse_adjacent([4,11,12,13]) == [4,(11,13)]
  assert collapse_adjacent([2,3])==[(2,3)]
  assert collapse_adjacent([1,3,5,6,7,8,10,12,13,14,16])==[1,3,(5,8),10,(12,14),16]

def test_address_phrase():
  assert address_phrase('A',[1])=='A1'
  assert address_phrase('B',[(3,7)])=='B3:B7'
  assert address_phrase('C',[1,(3,5),7,(9,11)])=='C1,C3:C5,C7,C9:C11'