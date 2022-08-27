'''tests formula handling'''
from dance.util.xl_formulas import table_ref

import pytest

def test_single_match():
  test='=@get_val("End Bal" &  [@AcctName],"tbl_balances",y_offset(this_col_name(),-1))'
  expected='=@get_val("End Bal" &  [[# this row],[@AcctName]],"tbl_balances",y_offset(this_col_name(),-1))'
  assert expected == table_ref(test)

def test_no_match():
  test='quick red fox etc'
  assert test == table_ref(test)

def test_spaces_in_name():
  test='something [@with a name] having spaces'
  expected='something [[# this row],[@with a name]] having spaces'
  assert expected == table_ref(test)

def test_multiple_different():
  test='[@AcctName],[@Type],[@Active]'
  expected='[[# this row],[@AcctName]],[[# this row],[@Type]],[[# this row],[@Active]]'
  assert expected == table_ref(test)

