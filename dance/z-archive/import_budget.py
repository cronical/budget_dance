from com.infinitekind.moneydance.model import BudgetItem
from com.infinitekind.moneydance.model import Account

import math

# to be run in Moneydance
# purpose is to import into budget
# input will be in csv file
# will replace the current budget items


#set up
book = moneydance.getCurrentAccountBook()
budget=book.getBudgets().findCurrentBudget()
items = budget.getItemList()

# remove the old items
while 0 < items.getItemCount():
  items.removeItem(items.getItem(0))

filename="/Users/george/argus/budget/bdg-inp.csv"
reqhdr = ['amount', 'category','interval',  'start',  'end']

noend= BudgetItem.INDEFINITE_END_DATE

#supported subset of interval codes
typecodes={'annually': BudgetItem.INTERVAL_ANNUALLY , 'weekly':BudgetItem.INTERVAL_WEEKLY ,'bi-weekly': BudgetItem.INTERVAL_BI_WEEKLY ,'bi-weekly (not prorated)': BudgetItem.INTERVAL_ONCE_BI_WEEKLY , 'semi-annually (not prorated)':BudgetItem.INTERVAL_ONCE_SEMI_ANNUALLY, 'annually (not prorated)':BudgetItem.INTERVAL_ONCE_ANNUALLY, 'semi-monthly':BudgetItem.INTERVAL_SEMI_MONTHLY,'monthly':BudgetItem.INTERVAL_MONTHLY , 'monthly (not prorated)': BudgetItem.INTERVAL_ONCE_MONTHLY ,'tri-monthly (not prorated)': BudgetItem.INTERVAL_ONCE_TRI_MONTHLY }



count=0

with open(filename, 'r') as csvfile:
  for row in csvfile:
    row=row.rstrip() # drop \r\n
    if len(row) > 0: # ignore blank rows
      if row[:1] != '#': # ignore comments
        vals=row.split(",")
        if count==0:
          #header
          if 5 != len(set(reqhdr)&set(vals)):
            raise ValueError('headers must include all and only: %s' % ', '.join(reqhdr))
          hdr=vals
        if count > 0:
          #everything else
          #todo add try except logic for rows with not enough elements
          #dates are assumed to be ISO strings like 20190101
          amt=float(vals[hdr.index("amount")])
          amt=int(math.floor(100*amt ))
          cat=vals[hdr.index("category")]
          acct = book.getRootAccount().getAccountByName(cat)
          if acct is None:
            raise ValueError('category is not found: %s' % cat)
          ivaltype=typecodes[vals[hdr.index("interval")].lower()]
          start=int(vals[hdr.index("start")])
          end=vals[hdr.index("end")]
          if 0==len(end):
            end=noend # default
          else:
            end=int(end)
          
          #write the row
          item=items.createItem()
          item.setAmount(amt)
          item.setTransferAccount(acct) # seems like it could error if category not there
          item.setInterval(ivaltype)
          item.setIntervalStartDate(start)
          item.setIntervalEndDate(end)
          print "Budget item added for %s"%(acct)
    
    count=count +1
print "%s rows processed"%(count)
if count > 0:
  items.saveEdits()

# display entire budget
for itm in items:
  amt=itm.getAmount()
  acct=itm.getTransferAccount()
  ivaltype=itm.getInterval()
  start=itm.getIntervalStartDate()
  end=itm.getIntervalEndDate()
  print "%d %s %d %d %d"%(amt,acct,start,end, ivaltype)

