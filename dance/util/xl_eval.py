'''Tools for preparation and evaluation of excel formulas
TODO prepare_formula is here instead of xl_formulas only to avoid dependency loop with tables.'''
import re
from openpyxl.formula import Tokenizer
from pandas import DataFrame


def filter_parser(formula):
  '''crude method to parse filter formula to be used to determine number of rows in the result
  
  Converts a formula of a excel dynamic array FILTER, possibly wrapped with a SORT to a list.
  Returns the table name, field name selected, and the list:
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
  table_name=matches[0]

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
  after_comma=False
  display_field=None
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
      if row.type == 'SEP':
        after_comma=True
      if row.type=='OPERAND':
        if row.subtype=='RANGE':
          matches=field_pat.search(row.value)
          field=matches.group(1)
          if after_comma:
            phrase_parsed[0]=field
          else:
            display_field=field
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
  return table_name, display_field, result

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
    table,field,parsed=filter_parser(formula)
    print(table,field,parsed)
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

def prepare_formula(formula):
  '''Utility method to strip array braces from a formula and
     also expand out dynamic array formulas.
     This does not fix the need for _xlpm. to prefix any parameters (declared or used) in a LAMBDA function'''
  # Remove array formula braces.
  if formula.startswith("{"):
    formula = formula[1:]
  if formula.endswith("}"):
    formula = formula[:-1]

  # Check if formula is already expanded by the user.
  if "_xlfn." in formula:
    return formula

  # Expand dynamic formulas.
  formula = re.sub(r"\bANCHORARRAY\(", "_xlfn.ANCHORARRAY(", formula)
  formula = re.sub(r"\bBYCOL\(", "_xlfn.BYCOL(", formula)
  formula = re.sub(r"\bBYROW\(", "_xlfn.BYROW(", formula)
  formula = re.sub(r"\bCHOOSECOLS\(", "_xlfn.CHOOSECOLS(", formula)
  formula = re.sub(r"\bCHOOSEROWS\(", "_xlfn.CHOOSEROWS(", formula)
  formula = re.sub(r"\bDROP\(", "_xlfn.DROP(", formula)
  formula = re.sub(r"\bEXPAND\(", "_xlfn.EXPAND(", formula)
  formula = re.sub(r"\bFILTER\(", "_xlfn._xlws.FILTER(", formula)
  formula = re.sub(r"\bHSTACK\(", "_xlfn.HSTACK(", formula)
  formula = re.sub(r"\bLAMBDA\(", "_xlfn.LAMBDA(", formula)
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

if __name__ == '__main__':
  test_filter_parser()