'''Utility programs that deal with Excel formulas'''
import re

def table_ref(formula):
  '''Allows user to specify formula using the short form of "a field in this row" by converting it
  to the long form which Excel recognizes exclusively (even though it displays the short form).

  args: formula using the short form such as [@AcctName]
  returns: formula using the long form such as [[#this row],[@AcctName]]
  '''

  result=formula
  regex=r'\[(@[ a-z0-9]+)\]'
  #regex=r'@[a-z]'
  p=re.compile(regex,re.IGNORECASE)
  for m in p.finditer(result):
    for g in m.groups():
      new='[#This Row],[{}]'.format(g[1:])
      result=result.replace(g,new)
  return result

def apply_formulas(table_info,data,ffy,is_actl):
  '''insert actual or forecast formulas per config
  The config may give formula definitions in sections called actl_formulas and/or fcst_formulas.
  If it exists, *_formulas section contains the key_field to use to match the key from the rules.
  The rules are a list of dictionaries that contain entries for 'key' and 'formula'.

  args: table_info portion of the config for this table
  data: a dataframe to modify
  ffy: the first forecast year as Ynnnn
  is_actl: True to apply the actual formulas, False to apply the forecast formulas

  returns: the possibly modified dataframe.
  '''
  section = ('fcst','actl')[int(is_actl)]  +'_formulas'
  if section not in table_info:
    return data
  rules=table_info[section]
  for rule in rules:
    base_field=rule['base_field']
    matches=rule['matches']
    if not isinstance(matches,list):
      matches=[matches]
    for ix, rw in data.loc[data[base_field].isin(matches)].iterrows(): # the rows that match this rule
      selector=is_actl
      for col in rw.index:
        if col == 'Y%d'%ffy:
          selector= not selector
        if selector:
          if col[0]=='Y' and col[1:].isnumeric():
            formula=table_ref(rule['formula'])
            data.at[ix,col]=formula
  return data

def actual_formulas(table_info,data,ffy):
  '''insert actual formulas per config
  The config may give a section called actl_formulas.
  If it exists, actl_formulas contains the key_field to use to match the key from the rules.
  The rules are a list of dictionaries that contain entries for 'key' and 'formula'.

  args: table_info portion of the config for this table
  data: a dataframe to modify
  ffy: the first forecast year as Ynnnn
  '''
  data=apply_formulas(table_info,data,ffy,True)
  return data

def forecast_formulas(table_info,data,ffy):
  '''insert forecast formulas per config
  The config may give a section called fcst_formulas.
  If it exists, fcst_formulas contains the key_field to use to match the key from the rules.
  The rules are a list of dictionaries that contain entries for 'key' and 'formula'.

  args: table_info portion of the config for this table
  data: a dataframe to modify
  ffy: the first forecast year as Ynnnn
  '''
  data=apply_formulas(table_info,data,ffy,False)
  return data

def dyno_fields(table_info,data):
  '''Apply dynamic field rules to data

  The config may give a section called dyno_fields.
  If it does it contains rules that allow creation of fields from other fields

  args: table_info portion of the config for this table
  data: a dataframe to modify

  returns: data, which may have been modified.
  '''
  if 'dyno_fields' not in table_info:
    return data
  rules=table_info['dyno_fields']
  for rule in rules:
    base_field=rule['base_field']
    matches=rule['matches']
    if not isinstance(matches,list):
      matches=[matches]
    if matches == ['*']: # special case if just a single *, meaning all
      selector= [True]*data.shape[0]
    else:
      selector=data[base_field].isin(matches)
    for ix, rw in data.loc[selector].iterrows(): # the rows that match this rule
      for action in rule['actions']:
        if 'constant' in action:
          value=action['constant']
        if 'suffix' in action:
          value= rw[base_field]+action['suffix']
        if 'formula' in action:
          value= table_ref(action['formula'])
        data.at[ix,action['target_field']]=value
  return data

def main():
  test='[@AcctName],[@Type],[@Active]'
  test='=@get_val("End Bal" &  [@AcctName],"tbl_balances",y_offset(this_col_name(),-1))'
  lf=table_ref(test)
  print(lf)

if __name__ == '__main__':
  main()
