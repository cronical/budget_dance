# Accounting Notes

## Accounts

### Opening and Closing of Accounts

The reference table in the spreadsheet is derived from the most recent data in the `acct-bals/` folder.  So adding accounts will work naturally. When accounts are closed their balance in Moneydance goes to zero.  By default, to avoid clutter, zero balance accounts are not included in the spreadsheet. In order to avoid the problem the account should be listed in the `include-zeros` section of the `config.yaml` file.  

### Banks

In Moneydance, there can be many bank accounts.  All of these are summarized into a single Bank Accounts planning account.  

### Passthru

In the chart of accounts Passthru is set up as a bank account, although it is entirely fictional.  Under this are sub-accounts, to help track various movements.  

1. A good example is an payroll deductions, which end up in another account, like a 401K.  Since both payroll and 401K systems allow transactions to be downloaded, it is convenient to run the offsetting transactions through a passthru subaccount, especially since the records show up at different times.  By doing this, each source can be reconciled independently.

1. For true transfers such as supporting a purchase or a sale, BuyXfr and SellXfr don't achieve the desired result. This is because the Transfers report does not include them. You must break out such events into two transactions -- one for the buy or sell and one for the transfer.

Of course, these transactions have to be doubled - i.e. one into the passthru account and one out.  In cases where this is not done, then provisions have to be made in the report definitions (e.g. the reports that transfer money in and out of investment accounts)

### Suspense

Similar to a passthru, but this is used to handle separate dividend and dividend reinvested transactions for some brokers (ML): 

A account suspense account may be used to support the way the broker handles re-investments.  The suspense account mimics the brokerage "reinvestment program", in that the dividends are sent out of the account to "reinvestment program" (aka our passthru subaccount) and then brought back in with a BuyXfr transaction on a date which may be the same as the dividend or different.  

## Credit Cards

Similar to banks, credit cards are clubbed together for budgeting purposes. 

## Movement of money

The general theory is that 

1. Income arrives in bank accounts
1. Expenses are paid through bank or credit card accounts
1. Credit cards are paid via bank accounts
2. Transfers in and out of investment accounts should go through a bank account via an `xfr` transaction. 



## Balances

The computation of balances depends on the ability to determine the changes to the accounts.  

### Tax advantaged accounts

## 529 Accounts

The tag `529-distr` is used to identify actual distributions.

## Health Savings Accounts (HSA)

Use the tag `hsa-distr` for all distributions. This allows selection of these no matter if the funds go to a bank (including passthru) or directly to the provider.

## Traditional IRA Accounts

IRA distributions are problematic.

The gross amount is taxable and thus needs to be included in the tax calculation.  However, the tax amounts go to the state and federal expense lines and the net goes to the receiving bank.  There is no place to declare income.

The solution allows a uniform way of handling the data (at the cost of a bit of special handling). 

The solution uses a Moneydance tag, `ira-txbl-distr` on those transactions.  This involves editing the transactions that are downloaded from the financial institution to add in the tag. This needs to be done in the Bank Register view not the Register view.  The tags field is only shown in the Bank Register view. Note the old mixed case version is shown.

![How it should look](assets/images/ira-txbl-distr.png)

## Roth IRA Accounts

Use the tag `roth-distr`.

## Tag support

The table `tbl_tag_sums` has been introduced to allow easy access to tagged transactions.  It can be selected based on Tag (single) and Account.  Multiple tags on a record are not supported (and believed detected, causing an error.)  

## Investments

The performance report provides opening and closing balances, income, gains and something called "Return Amount". It does not indicate unrealized gains per se.  The "Return Amount" is essentially a plug to get to the ending balance.  Note - income needs to be marked MiscInc (not transfer to the income category)

Gains are essentially realized gains. Fees for purchases and/or sales of securities are included as part of the cost basis.  Other fees, that occur outside of the purchase or sale transaction are not included - such things as commissions, other account fees, and others. 

The other fees are rolled into the plug field (Return Amount), along with unrealized gains. It is better to include them in the Gains and therefore the 'Rlz Int/Gn' value in the spreadsheet. Thus when an account is closed, there will be no unrealized gains. 

To do this the investment fees need two categories.  

- Investing:Action Fees, 
- Investing:Account Fees.  

Only the account fee is selected in the Investment IandE report.  This allows the loading of investment actuals to add the account fees to the gains.  It also means that the transaction fees are not used to forecast future fees.  This is reasonable since they are by nature not asset based and the forecast method uses percentage of assets.

### Technique

The action fees default to the account default, which is wrong.  Batch change does not work since it applies to the normal category, not the fee category. In order to batch change these "go to otherside" on a transaction that has an fee.  Typically this is a sell transaction.  Isolate the ones you want in that account and batch change the account to Investing:Action Fees.

## Other Assets

The "Other Asset" account has several sub-accounts, including receivables from a few parties.  The method of determining the transfers depends is to use the `transfers-to-fcast` memorized report.  Some of the sub-accounts in Other Asset have transactions using expense categories.  To support this the memorized report includes all expenses in the criteria.  This correctly gathers the amounts such as depreciation for cars and payments made against some expense category (on our behalf).  The set of a target accounts configured in this report includes all investment, loan, asset and liability accounts.   

Whenever there is a transfer between these accounts, this method essentially cancels out that values, which can lead to wrong balances.  Such transactions should be routed throught the `Passthru` bank account to avoid this problem.

