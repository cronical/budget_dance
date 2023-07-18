'''Utility programs that deal with Excel formulas'''
import re

from dance.util.logs import get_logger
from dance.util.sheet import df_for_range
from dance.util.xl_pm import get_params,repl_params

FUTURE_FUNCTIONS=[
  "ANCHORARRAY", "BYCOL", "BYROW", "CHOOSECOLS", "CHOOSEROWS", 
  "DROP", "EXPAND","FORECAST.LINEAR","FILTER","HSTACK", "LAMBDA", "LET", "MAKEARRAY",
  "MAP", "RANDARRAY", "REDUCE", "SCAN", "SINGLE", "SEQUENCE","SORT", "SORTBY", "SWITCH", 
  "TAKE", "TEXTSPLIT", "TOCOL", "TOROW", "UNIQUE","VSTACK","WRAPCOLS","WRAPROWS","XLOOKUP", 
  ]

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

def this_row(field):
  ''' prepare part of the formula so support Excel;s preference for the [#this row] style over the direct @
  '''
  return '[[#this row],[{}]]'.format(field)

def apply_formulas(table_info,data,ffy,is_actl,wb=None,table_map=None):
  '''insert actual or forecast formulas per config
  The config may give formula definitions in sections called actl_formulas, all_col_formulas and/or fcst_formulas.
  If it exists, *_formulas section contains the key_field to use to match the key from the rules.
  The rules are a list of dictionaries of two types both of which contain a 'formula'
    - contain an enumeration of the values to match, or
    - more complex queries

  args: table_info portion of the config for this table
  data: a dataframe to modify
  ffy: the first forecast year as Ynnnn
  is_actl: True to apply the actual formulas, False to apply the forecast formulas
  wb: the in-memory openpyxl workbook (needed for lookups against already established tables)
  table_map: the table to worksheet map (used for lookups)

  returns: the possibly modified dataframe.
  '''
  logger=get_logger(__file__)
  sections = ['all_col_formulas']+[('fcst','actl')[int(is_actl)]  +'_formulas']
  rules=[]
  for section in sections:
    if section not in table_info:
      continue
    rules+=table_info[section]
  for rule in rules:
    if 'matches' in rule:
      base_field=rule['base_field']
      matches=rule['matches']
      if not isinstance(matches,list):
        matches=[matches]
      selection=data[base_field].isin(matches)
    else:
      assert 'query' in rule,'neither matches or query is in the rule'
      queries=rule['query']
      selection = True
      for query in queries:
        assert query['compare_with'] in ['=','starts','not_starting', 'is_in'],'Nonce error - comparison not implemented '+query['compare_with']
        values=data[query['field']]
        if 'look_up' in query: # if its a lookup perform the lookup.  
          look_up=query['look_up']
          ref_table=look_up['table']
          source_ws=wb[table_map[ref_table]] 
          ref_df=df_for_range(worksheet=source_ws,range_ref=source_ws.tables[ref_table].ref) # The index is the 1st column in the table
          index_on=data[look_up["index_on"]]
          values=ref_df.loc[index_on,look_up['value_field']].reset_index(drop=True)# lookup with the index then discard it
        match query['compare_with']:
          case '=':
            next_sel=(values == query['compare_to'])
          case 'starts':
            next_sel=  values.str.startswith(query['compare_to'])
          case 'not_starting':
            next_sel= ~ values.str.startswith(query['compare_to'])
          case 'is_in':
            next_sel= values.isin(query['compare_to'])
        if next_sel.sum()==0:
            logger.warning('Formula not applied due to query producing no rows.')
            logger.warning('Query is: %s %s %s'% (query['field'],query['compare_with'],query['compare_to']))       
        selection=selection & next_sel
    for ix, rw in data.loc[selection].iterrows(): # the rows that match this rule
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

def actual_formulas(table_info,data,ffy,wb=None,table_map=None):
  '''insert actual formulas per config
  The config may give a section called actl_formulas.
  If it exists, actl_formulas contains the key_field to use to match the key from the rules.
  The rules are a list of dictionaries that contain entries for 'key' and 'formula'.

  args: table_info portion of the config for this table
  data: a dataframe to modify
  ffy: the first forecast year as Ynnnn
  '''
  data=apply_formulas(table_info,data,ffy,True,wb=wb,table_map=table_map)
  return data

def forecast_formulas(table_info,data,ffy,wb=None,table_map=None):
  '''insert forecast formulas per config
  The config may give a section called fcst_formulas.
  If it exists, fcst_formulas contains the key_field to use to match the key from the rules.
  The rules are a list of dictionaries that contain entries for 'key' and 'formula'.

  args: table_info portion of the config for this table
  data: a dataframe to modify
  ffy: the first forecast year as Ynnnn
  '''
  data=apply_formulas(table_info,data,ffy,False,wb=wb,table_map=table_map)
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

def is_formula(value):
  '''Returns true if the value is a formula'''
  result=False
  if value is not None:
    if isinstance(value,str):
      if value.startswith('='):
        result=True
  return result

def prepare_formula(formula):
  '''Utility method to:
      strip array braces from a formula, 
      fully qualify selected subset of "future functions (usually with _xlfn.), and
      qualify parameters of LET and LAMBDA with _xlpm." 
      returns possibly modified formula
  '''
  # Remove array formula braces.
  if formula.startswith("{"):
    formula = formula[1:]
  if formula.endswith("}"):
    formula = formula[:-1]

  # fix any parameters unless user has fixed at least one.
  if "_xlpm." not in formula:
    params=get_params(formula)
    formula=repl_params(formula,params)

  # Check if formula is already expanded by the user.
  if "_xlfn." in formula:
    return formula

  # from xls_writer with LET and LAMBDA added
  # Expand dynamic formulas.
  formula = re.sub(r"\bANCHORARRAY\(", "_xlfn.ANCHORARRAY(", formula)
  formula = re.sub(r"\bBYCOL\(", "_xlfn.BYCOL(", formula)
  formula = re.sub(r"\bBYROW\(", "_xlfn.BYROW(", formula)
  formula = re.sub(r"\bCHOOSECOLS\(", "_xlfn.CHOOSECOLS(", formula)
  formula = re.sub(r"\bCHOOSEROWS\(", "_xlfn.CHOOSEROWS(", formula)
  formula = re.sub(r"\bDROP\(", "_xlfn.DROP(", formula)
  formula = re.sub(r"\bEXPAND\(", "_xlfn.EXPAND(", formula)
  formula = re.sub(r"\bFORECAST.LINEAR\(", "_xlfn.FORECAST.LINEAR(", formula)
  formula = re.sub(r"\bFILTER\(", "_xlfn._xlws.FILTER(", formula)
  formula = re.sub(r"\bHSTACK\(", "_xlfn.HSTACK(", formula)
  formula = re.sub(r"\bLAMBDA\(", "_xlfn.LAMBDA(", formula)
  formula = re.sub(r"\bLET\(", "_xlfn.LET(", formula)
  formula = re.sub(r"\bMAKEARRAY\(", "_xlfn.MAKEARRAY(", formula)
  formula = re.sub(r"\bMAP\(", "_xlfn.MAP(", formula)
  formula = re.sub(r"\bRANDARRAY\(", "_xlfn.RANDARRAY(", formula)
  formula = re.sub(r"\bREDUCE\(", "_xlfn.REDUCE(", formula)
  formula = re.sub(r"\bSCAN\(", "_xlfn.SCAN(", formula)
  formula = re.sub(r"\SINGLE\(", "_xlfn.SINGLE(", formula)
  formula = re.sub(r"\bSEQUENCE\(", "_xlfn.SEQUENCE(", formula)
  formula = re.sub(r"\bSORT\(", "_xlfn._xlws.SORT(", formula)
  formula = re.sub(r"\bSORTBY\(", "_xlfn.SORTBY(", formula)
  formula = re.sub(r"\bSWITCH\(", "_xlfn.SWITCH(", formula)
  formula = re.sub(r"\bTAKE\(", "_xlfn.TAKE(", formula)
  formula = re.sub(r"\bTEXTSPLIT\(", "_xlfn.TEXTSPLIT(", formula)
  formula = re.sub(r"\bTOCOL\(", "_xlfn.TOCOL(", formula)
  formula = re.sub(r"\bTOROW\(", "_xlfn.TOROW(", formula)
  formula = re.sub(r"\bUNIQUE\(", "_xlfn.UNIQUE(", formula)
  formula = re.sub(r"\bVSTACK\(", "_xlfn.VSTACK(", formula)
  formula = re.sub(r"\bWRAPCOLS\(", "_xlfn.WRAPCOLS(", formula)
  formula = re.sub(r"\bWRAPROWS\(", "_xlfn.WRAPROWS(", formula)
  formula = re.sub(r"\bXLOOKUP\(", "_xlfn.XLOOKUP(", formula)
  return formula
