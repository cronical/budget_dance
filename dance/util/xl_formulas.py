'''Utility programs that deal with Excel formulas'''
import re

def table_ref(formula):
  '''Allows user to specify formula using the short form of "a field in this row" by converting it
  to the long form which Excel recognizes exclusively (even though it displays the short form).

  args: formula using the short form such as [@AcctName]
  returns: formula using the long form such as [[#this row],[@AcctName]]
  '''

  result=formula
  regex=r'(\[@[ a-z]+\])'
  #regex=r'@[a-z]'
  p=re.compile(regex,re.IGNORECASE)
  for m in p.finditer(result):
    for g in m.groups():
      new='[[# this row],{}]'.format(g)
      result=result.replace(g,new)
  return result

def main():
  test='[@AcctName],[@Type],[@Active]'
  lf=table_ref(test)
  print(lf)

if __name__ == '__main__':
  main()
