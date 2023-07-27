'''tests formula handling'''
import pandas as pd
from dance.util.xl_formulas import table_ref,prepare_formula
from dance.util.xl_pm import get_params,repl_params
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

def test_xl_pm():


  # LET
  formula='=LET(y,INDIRECT("tbl_balances["&INDEX(tbl_balances[#Headers],COLUMN())&"]"),a,[@AcctName],b,{"Start Bal","End Bal"},c,{"Rlz Int/Gn","Unrlz Gn/Ls"},x,MATCH(b&a,[Key],0),w,MATCH(c&a,[Key],0),2*SUM(CHOOSEROWS(y,w))/SUM(CHOOSEROWS(y,x)))'
  formula2='=LET(_xlpm.y,INDIRECT("tbl_balances["&INDEX(tbl_balances[#Headers],COLUMN())&"]"),_xlpm.a,[@AcctName],_xlpm.b,{"Start Bal","End Bal"},_xlpm.c,{"Rlz Int/Gn","Unrlz Gn/Ls"},_xlpm.x,MATCH(_xlpm.b&_xlpm.a,[Key],0),w,MATCH(_xlpm.c&_xlpm.a,[Key],0),2*SUM(CHOOSEROWS(_xlpm.y,_xlpm.w))/SUM(CHOOSEROWS(_xlpm.y,_xlpm.x)))'
  params=get_params(formula)
  assert params == ['y', 'a', 'b', 'c', 'x', 'w']
  formula='=LET(x,9,y,12,sum(x,y))'
  params=get_params(formula)
  assert params == ['x','y']
  
  # LAMBDA
  formula='=BYROW(Table2[[Y1]:[Y2]],LAMBDA(arr,MAX(arr)))'
  formula2='=BYROW(Table2[[Y1]:[Y2]],LAMBDA(_xlpm.arr,MAX(_xlpm.arr)))'
  params=get_params(formula)
  assert params == ['arr']
  assert repl_params(formula,params)== formula2
  
  formula='=LAMBDA(a,b, SQRT((a^2)+(b^2)))(3,4)'
  formula2='=LAMBDA(_xlpm.a,_xlpm.b, SQRT((_xlpm.a^2)+(_xlpm.b^2)))(3,4)'
  params=get_params(formula)
  assert params == ['a','b']
  assert repl_params(formula,params)== formula2

  formula='=SUM(BYROW((tbl_transfers_plan[[From_Account]:[To_Account]]=tbl_balances[@AcctName])*HSTACK(-tbl_transfers_plan[Amount],tbl_transfers_plan[Amount]),LAMBDA(row,SUM(row)))*(tbl_transfers_plan[Y_Year]=this_col_name()))'
  formula2='=SUM(BYROW((tbl_transfers_plan[[From_Account]:[To_Account]]=tbl_balances[@AcctName])*HSTACK(-tbl_transfers_plan[Amount],tbl_transfers_plan[Amount]),LAMBDA(_xlpm.row,SUM(_xlpm.row)))*(tbl_transfers_plan[Y_Year]=this_col_name()))'
  params=get_params(formula)
  assert params == ['row']
  assert repl_params(formula,params) == formula2

  # both (nested LAMBDA in LET)
  formula='=LET(a,BYROW(Table2[[Y1]:[Y2]],LAMBDA(arr,MAX(arr))),SUM(a))'
  formula2='=LET(_xlpm.a,BYROW(Table2[[Y1]:[Y2]],LAMBDA(_xlpm.arr,MAX(_xlpm.arr))),SUM(_xlpm.a))'
  params=get_params(formula)
  assert params == ['a','arr']
  assert repl_params(formula,params)== formula2
  


  # NONE
  formula='=SUM(3,4)'
  formula2='=SUM(3,4)'
  params=get_params(formula)
  assert params == []
  assert repl_params(formula,params)== formula2

def test_prepare_formula():
  formula='=XLOOKUP("End Bal"&tbl_retir_vals[@Item],tbl_balances[Key],CHOOSECOLS(tbl_balances[#Data],XMATCH(this_col_name(),tbl_balances[#Headers])-1)) *(1+tbl_retir_vals[@[Anny Rate]])*(YEAR(tbl_retir_vals[@[Start Date]])=THIS_YEAR())'
  formula2='=_xlfn.XLOOKUP("End Bal"&amp;tbl_retir_vals[[#This Row],[Item]],tbl_balances[Key],_xlfn.CHOOSECOLS(tbl_balances[#Data],_xlfn.XMATCH(this_col_name(),tbl_balances[#Headers])-1)) *(1+tbl_retir_vals[[#This Row],[Anny Rate]])*(YEAR(tbl_retir_vals[[#This Row],[Start Date]])=THIS_YEAR())'
  f=prepare_formula(formula)
  f=f=table_ref(f)
  f=f.replace("&","&amp;")
  assert f == formula2

  # portion
  formula = '=LAMBDA(s,e,y,DAY_COUNT(MAX_MIN(VSTACK(HSTACK(s,DEFAULT_DATE(e)),FIRST_LAST(y))))/DAY_COUNT(FIRST_LAST(y)))'
  formula2='=_xlfn.LAMBDA(_xlpm.s,_xlpm.e,_xlpm.y,DAY_COUNT(MAX_MIN(_xlfn.VSTACK(_xlfn.HSTACK(_xlpm.s,DEFAULT_DATE(_xlpm.e)),FIRST_LAST(_xlpm.y))))/DAY_COUNT(FIRST_LAST(_xlpm.y)))'
  f=prepare_formula(formula)
  assert f == formula2
  pass  