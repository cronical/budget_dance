'''Utility programs that deal with Excel formulas'''
import re

def table_ref(formula):
  '''Allows user to specify formula using the short form of "a field in this row" by converting it
  to the long form which Excel recognizes exclusively (even though it displays the short form).
  Does not support spaces in field names

  args: formula using the short form such as [@AcctName]
  returns: formula using the long form such as [[#this row],[@AcctName]]
  '''

  result=formula
  regex=r'(\[@\[?[ a-z0-9]+\]?\])' # the inner escaped brackets allow for fields that have spaces in their names 
  #regex=r'@[a-z]'
  p=re.compile(regex,re.IGNORECASE)
  for m in p.finditer(result):
    for g in m.groups():
      h=str(g)
      for punc in '@[]':
        h=h.replace(punc,'')
      new='[[#This Row],[{}]]'.format(h)
      result=result.replace(g,new)
  return result

def apply_formulas(table_info,data,ffy,is_actl):
  '''insert actual or forecast formulas per config
  The config may give formula definitions in sections called actl_formulas, all_col_formulas and/or fcst_formulas.
  If it exists, *_formulas section contains the key_field to use to match the key from the rules.
  The rules are a list of dictionaries that contain entries for 'key' and 'formula'.

  args: table_info portion of the config for this table
  data: a dataframe to modify
  ffy: the first forecast year as Ynnnn
  is_actl: True to apply the actual formulas, False to apply the forecast formulas

  returns: the possibly modified dataframe.
  '''
  sections = ['all_col_formulas']+[('fcst','actl')[int(is_actl)]  +'_formulas']
  rules=[]
  for section in sections:
    if section not in table_info:
      continue
    rules+=table_info[section]
  for rule in rules:
    base_field=rule['base_field']
    matches=rule['matches']
    if not isinstance(matches,list):
      matches=[matches]
    for ix, rw in data.loc[data[base_field].isin(matches)].iterrows(): # the rows that match this rule
      selector=is_actl
      yix=0 # special handling if first year: allow it to be skipped such as for a start bal, or have its own value.
      first_item=None
      if 'first_item'in rule:
        first_item=str(rule['first_item'])
        # it is now always a list
        if first_item=='skip' or first_item.startswith('='):
          first_item=[first_item]
        else:
          first_item=first_item.split(',')
      for col in rw.index:
        if col == 'Y%d'%ffy:
          selector= not selector
        if selector:
          if col[0]=='Y' and col[1:].isnumeric():
            formula=table_ref(rule['formula'])
            if first_item is not None:
              if yix in range(len(first_item)):
                if yix==0 and first_item[0]=='skip':
                  yix=+1
                  continue
                if yix==0 and first_item[0].startswith('='):
                  formula=table_ref(first_item[0])
                else:
                  formula='='+first_item[yix]
            yix+=1
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
