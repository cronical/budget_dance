'''Utility programs that deal with Excel formulas'''
import re
from openpyxl.formula import Tokenizer
from pandas import DataFrame

def table_ref(formula):
  '''Allows user to specify formula using the short form of "a field in this row" by converting it
  to the long form which Excel recognizes exclusively (even though it displays the short form).
  Supports spaces in field names

  args: formula using the short form such as [@AcctName] or tbl_name[column_name]
  returns: formula using the long forms such as [[#this row],[@AcctName]]
  '''

  regex_row=r'\[@\[?([ A-Za-z0-9]+)\]?\]' 
  # the inner escaped brackets allow for fields that have spaces in their names 
  # the @ indicates - it refers to this row
  # otherwise its the whole column, which seems to work fine without convering to the [[#Data],[column]] form.   
  result=formula
  result=re.sub(regex_row,r'[[#This Row],[\1]]',result)
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

def filter_parser(formula):
  '''crude method to parse filter formula to be used to determine number of rows in the result
  
  Converts a formula of a excel dynamic array FILTER, possibly wrapped with a SORT to a list.
  The items on the even indices are 3 element lists - the last two which may be None:
    field, a comparison operator, and compare to value
  Items on the odd indicies are of length 1, inhabited by a join symbol (and/or)
  
  This is quite limited and is intended to provide only a work around for openpyxl's lack of dynamic array support.
  For filters with more than one criteria, use parentheses around each criteria.
  
  '''

  field_pat=re.compile('\[([\w ]+)\]')

  table_pat=re.compile('tbl_[a-zA-Z0-9]+')
  matches=table_pat.findall(formula)
  assert 1==len(set(matches)),'Formula does not refer to exactly one table'

  tok=Tokenizer(formula)
  toks=[]
  for t in tok.items:
    toks.append({"value":t.value,"type":t.type,"subtype":t.subtype})
  df= DataFrame(toks)

  df['open']=(df.subtype=='OPEN')*1
  df['close'] =((df.subtype=='CLOSE')*-1).shift(periods=1,fill_value=0)
  df['cum']=(df.open+df.close).cumsum()
  df['phrase_nums']=(df.cum != df.cum.shift(fill_value=0)).cumsum()

  result=[]
  in_filter=False
  for i in df.phrase_nums.unique():
    phrase_parsed=[None,None,None]
    phrase=df.loc[df.phrase_nums==i]
    for _,row in phrase.iterrows():
      if row.type == 'FUNC':
        if row.value=='FILTER(':
          in_filter=True
      if row.subtype == 'CLOSE':
        if in_filter:
          if phrase_parsed[0] is not None:
            result.append(phrase_parsed)
          if row.type == 'FUNC':
            in_filter=False # assume no functions internal to FILTER
      if row.type=='OPERAND':
        if row.subtype=='RANGE':
          matches=field_pat.search(row.value)
          field=matches.group(1)
          phrase_parsed[0]=field
        else:
          val=row.value
          if row.subtype=='NUMBER':
              val=int(row.value) # assumes no decimal places are given
          if row.subtype=='TEXT':
            val=val.replace('"','')
          phrase_parsed[2]=val
      if row.type == 'OPERATOR-INFIX':
        if phrase.shape[0]!=1:
          phrase_parsed[1]=row.value
        else:
          result.append([row.value]) # this is the and or or (+ or *)
  return result

def test_filter_parser():
  cases=[
      '=FILTER(tbl_accounts[Account],tbl_accounts[Active]*tbl_accounts[No Distr Plan])',
      '=FILTER(tbl_accounts[Account],(tbl_accounts[Active])*(tbl_accounts[No Distr Plan]))',
      '=FILTER(tbl_accounts[Account],(tbl_accounts[Active]=1)*(tbl_accounts[No Distr Plan]=1))',
      '=FILTER(tbl_accounts[Account],tbl_accounts[Active])',
      '=FILTER(tbl_accounts[Account],(tbl_accounts[Type]="I")+(tbl_accounts[Type]="B"))',
      '=SORT(FILTER(tbl_accounts[Account],tbl_accounts[Active]))',
      '=SORT(FILTER(tbl_accounts[Account],(tbl_accounts[Active])*(tbl_accounts[No Distr Plan])))',
      '=FILTER(tbl_accounts[Account],tbl_accounts[Active]=1)',
      '=FILTER(tbl_accounts[Account],(tbl_accounts[Active]=1))',
      '=FILTER(tbl_accounts[Account],(tbl_accounts[Active]=1)*(tbl_accounts[No Distr Plan]=1))'
  ]

  for formula in cases:
    print(formula)
    r=filter_parser(formula)
    print(r)
    print ("")

def eval_criteria(criteria,ref_df):
    '''given criteria from filter_parser and the reference table
    return a boolean series that selects the records defined by the criteria'''
    left=None
    op=None
    for ix,criterion in enumerate(criteria):
        if 0== ix %2:
            field,infix,val=criterion
            if infix is None: # default
                infix='='
                val=1
            assert infix=='=', 'Nonce: only equality supported, not '+infix
            sel=ref_df[field] == val
            if left is None:
                left=sel
            if op is not None:
                match op:
                    case '+':
                        left=left | sel
                    case '*':
                        left=left & sel
        else:
            assert len(criterion)==1, 'Expected just and or or, not ' + str(criterion)
            op=criterion[0]
            assert op in '+*', 'Expected + or * not ' + op            
    return left


def main():
  test='[@AcctName],[@Type],[@Active]'
  test='=@get_val("End Bal" &  [@AcctName],"tbl_balances",y_offset(this_col_name(),-1))'
  lf=table_ref(test)
  print(lf)

if __name__ == '__main__':
  test_filter_parser()
