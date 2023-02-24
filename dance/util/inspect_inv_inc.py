'''Python script to be run in Moneydance

purpose is to find transactions that are income but not categorized as such properly
2/23/23
'''
from com.infinitekind.moneydance.model import AbstractTxn, InvestTxnType# type: ignore

root = moneydance.getCurrentAccount() # type: ignore pylint: disable=undefined-variable
book = moneydance.getCurrentAccountBook()# type: ignore pylint: disable=undefined-variable

# set the date range and types action codes
DATE_LOW=20220101
DATE_HIGH=20221231
TRANS_ACTIONS=[InvestTxnType.SELL,InvestTxnType.SELL_XFER,InvestTxnType.MISCINC]

def split_type_map (parent_txn):
  '''map the splits by invest.splittype.  The keys in the resulting map are the values such as 'sec' and 'xfr'
  the values in the map are the split numbers
  uses the tags on the main transaction
 '''
  tags= parent_txn.getTags()
  split_map=dict()
  for i in (0,parent_txn.getSplitCount()-1):
    d= "%d.%s"%(i, AbstractTxn.TAG_INVST_SPLIT_TYPE)
    if d in tags:
      split_map.update({tags[d]:i})
  return split_map


accounts=root.getSubAccounts()

print("List income transactions")
#account_names=['401K - GBD - TRV','401K - VEC - UHG','CHET - Fidelity',
#               'HSA - GBD - Fidelity','HSA - VEC - UHG',
#               'IRA - GBD - Vanguard','IRA - VEC - ML','IRA - VEC - Vanguard',
#               'IRA Roth - GBD - Vanguard','IRA Roth - VEC - Vanguard'] 
for account in accounts:
  #account = root.getAccountByName(account_name)
  if account.getAccountType()==account.AccountType.INVESTMENT:
    if not account.getAccountIsInactive():
      print ("\nAccount:  %s " % account.getAccountName())
      print ("-"*(10+len(account.getAccountName())))
      txns = book.getTransactionSet().getTransactionsForAccount(account)
      for txn in txns.iterator():
        isParent = txn.getParentTxn()==txn #this is a parent not a split
        if isParent:
          txnStat=txn.getStatus()
          txnDate=txn.getDateInt()
          if (DATE_LOW<=txnDate) & (DATE_HIGH>=txnDate):
            txnDescr = txn.getDescription()
            txnAmt = txn.getValue()
            itt= txn.getInvestTxnType()
            if itt in TRANS_ACTIONS:
              print("%d\t%s\t%d\t\t%s"%(txnDate,txn.getInvestTxnType(),txn.getValue(),txn.getDescription()))
              code_map =split_type_map(txn)
              for code,value in code_map.items():
                other=txn.getOtherTxn(value)
                print("\t\t\t%d\t%s"%(other.getValue(),other.getAccount()))
