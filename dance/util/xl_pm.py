#! /usr/bin/env python
'''Try to add qualifiers for let and lambda'''
import re
import logging
from openpyxl.formula import Tokenizer
import pandas as pd
from dance.util.logs import get_logger
logger=get_logger(__file__,logging.INFO)

moduli={"LAMBDA":1,"LET":2} # which parameters we keep 
sf='|'.join(moduli.keys())
SUPPORTED_FNS='(%s)'%sf # regex style

def mark_parms(df,start_row=0,caller_scope=None):
  '''walk through the dataframe starting at index ix,
  dataframe is value,type,subtype,parameter, with sequential index
  the index must point to a row in the dataframe
  caller_scope is None unless the function in the formula that is calling is one of the supported functions
  modifies parameter colum for operands that meet criteria to be True
  returns next index and modified dataframe
  '''
  comma_count=0
  ix=start_row
  val,typ,subtyp,_ = df.loc[ix]
  scope=None
  while ix < df.shape[0]:
    val,typ,subtyp,_ = df.loc[ix]
    logger.debug('%s, %s, %s, %d'%(val,typ,subtyp,ix))  
    if (subtyp=='OPEN'):
      if (typ=='FUNC') :
        scope= re.search(SUPPORTED_FNS,val,re.IGNORECASE) # will be None if not found
        # otherwise to get the function:           scope.group(0), 
      ix,df=mark_parms(df,ix+1,scope) # 

    else:  
      if subtyp=='CLOSE':
          return (ix+1),df
      if typ=='SEP' and caller_scope is not None:
        comma_count +=1
        ix += 1
        continue
      ix += 1
    if typ in['OPERAND',"FUNC"]:
      if df.at[ix-1,'subtype']=='RANGE' and caller_scope is not None:   
        # the range clause prevents final parameter from being captured (as it is the result of the formula)
        if 0==comma_count%moduli[caller_scope.group(0).upper()]:  # only for LET (not sure about LAMBDA) TODO
          df.at[ix-1,'parameter']=True # ix has already be incremented

  return ix,df

def get_params(formula):
  '''Given a formula return the parameters that need to be prefaced by _xlpm.
  Requires formula to start with ='''
  try:
    tok=Tokenizer(formula)
  except IndexError:
    logger.error("Bad formula: %s"% formula)
    raise IndexError("Bad formula")  
  toks=[]
  for t in tok.items:
    toks.append({"value":t.value,"type":t.type,"subtype":t.subtype})
  df= pd.DataFrame(toks)
  df['parameter']=False
  _,df=mark_parms(df)
  params=list(pd.unique(df.loc[df.parameter,'value']))
  return params  

def repl_params(formula,params):
  '''replace each of the parameters given with the parm prepended with _xlpm.'''
  for p in params:
    pat=r"\b"+p+r"\b"
    new= "_xlpm."+p
    formula=re.sub(pat,new,formula)
  return formula

if __name__=="__main__":
  formula='=SUM(BYROW((tbl_transfers_plan[[From_Account]:[To_Account]]=tbl_balances[@AcctName])*HSTACK(-tbl_transfers_plan[Amount],tbl_transfers_plan[Amount]),LAMBDA(row,SUM(row)))*(tbl_transfers_plan[Y_Year]=this_col_name()))'
  formula='=LET(a,BYROW(Table2[[Y1]:[Y2]],LAMBDA(arr,MAX(arr))),SUM(a))'
  formula='=LET(y,INDIRECT("tbl_balances["&INDEX(tbl_balances[#Headers],COLUMN())&"]"),a,[@AcctName],b,{"Start Bal","End Bal"},c,{"Rlz Int/Gn","Unrlz Gn/Ls"},x,MATCH(b&a,[Key],0),w,MATCH(c&a,[Key],0),2*SUM(CHOOSEROWS(y,w))/SUM(CHOOSEROWS(y,x)))'
  params=get_params(formula)
  logger.info('{}'.format(params))
  logger.info(repl_params(formula,params))
    
