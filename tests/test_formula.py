'''tests formula handling'''
from dance.util.xl_formulas import table_ref

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

