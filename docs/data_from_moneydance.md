# Generating reports for data

Each of the reports [reports table](./data_files.md) should be run for the appropriate period and the output exported as a .tsv file and saved in the data folder or a subfolder, under the name given in the [table](./data_files.md)

The `dance/build` shell script will completely rebuild the worksheet. Or the following utilities can rebuild portions.

|Utility|Purpose|
|---|---|
|`dance/iande-actl-load.py`||
|`dance/transfers_actl_load.py`||
|`dance/invest_actl_load.py`||
|`dance/accounts_load.py`||
|`dance/balances_load.py`||
|`dance/bank_actl_load.py`||
|`dance/iande_actl_load.py`||
|`dance/invest_actl_load.py`||
|`dance/invest_iande_load.py`||
|`dance/other_actls.py`||
|`dance/retire_load.py`||
|`dance/taxes_load.py`||
|`dance/transfers_actl_load.py`||





   * IRA distributions are problematic [see note IRA-Txbl-Distr](./sheets/other_actl.md#ira-distributions).

## First pass on the taxes 

The first pass does not rely on the tax forms, those come later - basically the bits that are not accounted for are entered into the manual_actl tab.

## Validate balances for a year

The routine `balance_check.py` is available to see how the values from the `Account Balances` report in Moneydance match to those in `test_wb.xlsx`. 

1. In Moneydance run the `Account Balances` report selecting all accounts. 
2. Save the report  under the names: `data/acct-bals-yyyy.tsv`.
3. If the year has rolled over in the spreadsheet
  - change first_forecast_year in on the tables worksheet.
3. In a terminal window set current directory to the project root and run `dance/balance_check.py yyyy` where yyyy is the year to check.  You should get a listing that shows the exact matches and the accounts that don't match (and how much they are off).




## Accounting

The computation of balances depends on the ability to determine the changes to the accounts.  

### Investments

The performance report provides opening and closing balances, income, gains and something called "Return Amount". It does not indicate unrealized gains per se.  The "Return Amount" is essentially a plug to get to the ending balance.  Note - income needs to be marked MiscInc (not transfer to the income category)

Gains are essentially realized gains. Fees for purchases and/or sales of securities are included as part of the cost basis.  Other fees, that occur outside of the purchase or sale transaction are not included - such things as commissions, other account fees, and others. 

The other fees are rolled into the plug field (Return Amount), along with unrealized gains. It is better to include them in the Gains and therefore the 'Rlz Int/Gn' value in the spreadsheet. Thus when an account is closed, there will be no unrealized gains. 

To do this the investment fees need two categories.  Investing:Action Fees, Investing:Account Fees.  Only the account fee is selected in the Investment IandE report.  This allows the loading of investment actuals to add the account fees to the gains.  It also means that the transaction fees are not used to forecast future fees.  This is reasonable since they are by nature not asset based and the forecast method uses percentage of assets.

### Other Assets

The "Other Asset" account has several sub-accounts, including receivables from a few parties.  The method of determining the transfers depends is to use the `transfers-to-fcast` memorized report.  Some of the sub-accounts in Other Asset have transactions using expense categories.  To support this the memorized report includes all expenses in the criteria.  This correctly gathers the amounts such as depreciation for cars and payments made against some expense category (on our behalf).  The set of a target accounts configured in this report includes all investment, loan, asset and liability accounts.   Whenever there is a transfer between these accounts, this method essentially cancels out that values, which can lead to wrong balances.  Such transactions should be routed throught the `Passthru` bank account to avoid this problem.

