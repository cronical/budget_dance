from com.infinitekind.moneydance.model import Account
from com.infinitekind.moneydance.model import InvestTxnType
from com.infinitekind.moneydance.model import TxnUtil
from com.infinitekind.moneydance.model import InvestFields

import math

# EXPERIMENTAL
# to be run in Moneydance
# display historical investment dividends etc

#set up
book = moneydance.getCurrentAccountBook()
root=book.getRootAccount()
accts = root.getSubAccounts()
filename="/Users/george/argus/budget/divhistory.csv"
count=0
with open(filename,'w')as csvfile:
  csvfile.write( 'account,month,day,type,amount\n')
  for acct in accts:
    name=acct.getAccountName()
    typ =acct.getAccountType()
    INVESTMENT=Account.AccountType.INVESTMENT
    if typ==INVESTMENT:
      if not acct.getAccountOrParentIsInactive():
        
        tSet = book.getTransactionSet().getTransactionsForAccount(acct)
        for txn in tSet.iterator():
          txnDate = txn.getDateInt()
          txnMo=txnDate/100
          txnDay= txnDate % 100
          if txnDate >= 20180101:
            txnTType= txn.getTransferType().split('_')[1]
          
            if (txnTType == 'dividend') or (txnTType== 'miscincexp'):
              txnDescr = txn.getDescription()
              txnMemo=txn.getMemo()
              txnVal=txn.getValue()
              inc=TxnUtil.getIncomePart(txn)
              incVal=-float(inc.getValue())/100
              sec=TxnUtil.getSecurityPart(txn)
              secDescr = sec.getDescription()
              csvfile.write( '%s,%d,%d,%s,%10.2f\n'%(name,txnMo,txnDay,txnTType,  incVal))
              count = count + 1
  csvfile.close()
print "%d items exported to %s" % (count,filename)


