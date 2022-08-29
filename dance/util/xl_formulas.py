'''Utility programs that deal with Excel formulas'''
import re

def table_ref(formula):
  '''Allows user to specify formula using the short form of "a field in this row" by converting it
  to the long form which Excel recognizes exclusively (even though it displays the short form).

  args: formula using the short form such as [@AcctName]
  returns: formula using the long form such as [[#this row],[@AcctName]]
  '''

  result=formula
  regex=r'\[(@[ a-z]+)\]'
  #regex=r'@[a-z]'
  p=re.compile(regex,re.IGNORECASE)
  for m in p.finditer(result):
    for g in m.groups():
      new='[#This Row],[{}]'.format(g[1:])
      result=result.replace(g,new)
  return result


def forecast_formulas(table_info,data,ffy):
  '''insert forecast formulas per config
  The config may give a section called fcst_formulas.
  If it does it contains the key_field to use to match the key from the rules.
  The rules are a list of dictionaries that contain entries for 'key' and 'formula'.

  args: table_info portion of the config for this table
  data: a dataframe to modify
  ffy: the first forecast year as Ynnnn
  '''

  if 'fcst_formulas' not in table_info:
    return data
  rules=table_info['fcst_formulas']
  for rule in rules:
    base_field=rule['base_field']
    matches=rule['matches']
    if not isinstance(matches,list):
      matches=[matches]
    for ix, rw in data.loc[data[base_field].isin(matches)].iterrows(): # the rows that match this rule
      fcst=False
      for col in rw.index:
        if col == 'Y%d'%ffy:
          fcst= True
        if fcst:
          formula=table_ref(rule['formula'])
          data.at[ix,col]=formula
  return data

def main():
  test='[@AcctName],[@Type],[@Active]'
  test='=@get_val("End Bal" &  [@AcctName],"tbl_balances",y_offset(this_col_name(),-1))'
  lf=table_ref(test)
  print(lf)

if __name__ == '__main__':
  main()
