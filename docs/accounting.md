# Accounting Notes

## Balances

The computation of balances depends on the ability to determine the changes to the accounts.  

## IRAs

IRA distributions are problematic.

The gross amount is taxable and thus needs to be included in the tax calculation.  However, the tax amounts go to the state and federal expense lines and the net goes to the receiving bank.  There is no place to declare income.

The solution allows a uniform way of handling the data (at the cost of a bit of special handling). 

The solution uses a Moneydance tag, `IRA-Txbl-Distr` on those transactions.  This involves editing the transactions that are downloaded from the financial institution to add in the tag. This needs to be done in the Bank Register view not the Register view.  The tags field is only shown in the Bank Register view. 

## Investments

The performance report provides opening and closing balances, income, gains and something called "Return Amount". It does not indicate unrealized gains per se.  The "Return Amount" is essentially a plug to get to the ending balance.  Note - income needs to be marked MiscInc (not transfer to the income category)

Gains are essentially realized gains. Fees for purchases and/or sales of securities are included as part of the cost basis.  Other fees, that occur outside of the purchase or sale transaction are not included - such things as commissions, other account fees, and others. 

The other fees are rolled into the plug field (Return Amount), along with unrealized gains. It is better to include them in the Gains and therefore the 'Rlz Int/Gn' value in the spreadsheet. Thus when an account is closed, there will be no unrealized gains. 

To do this the investment fees need two categories.  

- Investing:Action Fees, 
- Investing:Account Fees.  

Only the account fee is selected in the Investment IandE report.  This allows the loading of investment actuals to add the account fees to the gains.  It also means that the transaction fees are not used to forecast future fees.  This is reasonable since they are by nature not asset based and the forecast method uses percentage of assets.

## Other Assets

The "Other Asset" account has several sub-accounts, including receivables from a few parties.  The method of determining the transfers depends is to use the `transfers-to-fcast` memorized report.  Some of the sub-accounts in Other Asset have transactions using expense categories.  To support this the memorized report includes all expenses in the criteria.  This correctly gathers the amounts such as depreciation for cars and payments made against some expense category (on our behalf).  The set of a target accounts configured in this report includes all investment, loan, asset and liability accounts.   

Whenever there is a transfer between these accounts, this method essentially cancels out that values, which can lead to wrong balances.  Such transactions should be routed throught the `Passthru` bank account to avoid this problem.

