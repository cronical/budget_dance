# Data from Moneydance

## Copy Income and Expense from Moneydance

1. In Moneydance run `Income & Expense by Year`
2. Save as `data/iande.tsv` 
3. Close spreadsheet and run the program  `iande-actl-load.py` 
4. Ensure that the formulas on the year are set to `getval...`
5. Check that income, tax and expense totals match to report: 
   * start at level 3 and drill down to find problems.
   * IRA distributions are problematic [see note IRA-Txbl-Distr](./workbook.md#ira-txbl-distr)
   * If there are new categories - you will need to insert a line

## First pass on the taxes 

The first pass does not rely on the tax forms, those come later - basically the bits that are not accounted for are entered into the manual_actl tab.

1. Check W2 exclusions on aux
2. Change the column for the year to use the actuals
3. Carefully check the progression of the logic

## Copy transfers data from Moneydance

1. Run report in Moneydance [currently called Transfers-to-fcast](./report_configs.md#transfers-to-fcast) for all actual periods.
2. Press Save button and choose Tab delimited and save as `data/transfers.tsv`
3. (If a year has been completed run the Bank balance export procedure)
4. If `fcast.xlsm` is open, save your work and close the file.
5. Open a terminal window at the project root.
6. Run `python transfers_actl_load.py`
7. Re-open the spreadsheet and save it to force balances to recalc and be stored.

```bash
> dance/transfers_actl_load.py
2022-08-19 12:49:34,546 - transfers_actl_load - INFO - loaded dataframe from data/transfers.tsv
2022-08-19 12:49:34,839 - tables - INFO - Read table tbl_iande_actl from data/fcast.xlsm
2022-08-19 12:49:34,839 - tables - INFO -   300 rows and 6 columns
2022-08-19 12:49:35,124 - transfers_actl_load - INFO - loaded workbook from data/fcast.xlsm
2022-08-19 12:49:35,162 - transfers_actl_load - INFO - First forecast year is: 2022
2022-08-19 12:49:35,470 - books - INFO - deleted worksheet transfers_actl
2022-08-19 12:49:35,470 - books - INFO - created worksheet transfers_actl
2022-08-19 12:49:35,499 - tables - INFO - table tbl_transfers_actl added to transfers_actl
```

## Bank balance export procedure

The method used is the difference of progressive balances.  This is done for each year.  

1. In Moneydance run the `Account Balances` report selecting only banks and credit cards.  
2. Save the file as tab-separated under `budget/data` as `bank-bal-YYYY`.
3. These files are consumed by the `transfers_actl_load.py` routine.

## Investment actuals

The Tranfers to Investment Accounts by Year report is saved as `invest-x.tsv`. The Investment Performance report for each year is saved under `invest-p-yyyy.tsv` for each year. These are processed by `invest_actl_load.py`. At each year end:

1. Run [Tranfers to Investment Accounts by Year](./report_configs.md#tranfers-to-investment-accounts-by-year) and save as `invest_x.tsv`
1. For each year:
   2. Run `Investment Performance` report for the year and save under `invest-p-yyyy.tsv`
   3. If `fcast.xlsm` is open, save your work and close the file.
   5. Open a terminal window at the project root.
   6. Run `invest_actl_load.py`
   7. Re-open the spreadsheet and save it to force balances to recalc and be stored.

```bash
>dance/invest_actl_load.py 
2022-08-19 13:49:22,563 - invest_actl_load - INFO - loaded dataframe from data/invest_x.tsv
2022-08-19 13:49:22,563 - invest_actl_load - INFO - Starting investment actual load
2022-08-19 13:49:22,824 - tables - INFO - Read table tbl_accounts from data/fcast.xlsm
2022-08-19 13:49:22,824 - tables - INFO -   27 rows and 10 columns
2022-08-19 13:49:22,834 - invest_actl_load - INFO - Processing 2018
2022-08-19 13:49:22,846 - invest_actl_load - INFO - Processing 2019
2022-08-19 13:49:22,856 - invest_actl_load - INFO - Processing 2020
2022-08-19 13:49:22,867 - invest_actl_load - INFO - Processing 2021
2022-08-19 13:49:23,145 - books - INFO - deleted worksheet invest_actl
2022-08-19 13:49:23,145 - books - INFO - created worksheet invest_actl
2022-08-19 13:49:23,175 - tables - INFO - table tbl_invest_actl added to invest_actl
```

## Validate balances for a year

The routine `balance_check.py` is available to see how the values from the `Account Balances` report in Moneydance match to those in `fcast.xlsm`. 

1. In Moneydance run the `Account Balances` report selecting all accounts. 
2. Save the report  under the names: `data/acct-bals-yyyy.tsv`.
3. If the year has rolled over in the spreadsheet
  - change first_forecast_year in on the tables worksheet.
3. In a terminal window set current directory to the project root and run `dance/balance_check.py yyyy` where yyyy is the year to check.  You should get a listing that shows the exact matches and the accounts that don't match (and how much they are off).



## Add an account

It may be best to do this by recreating the worksheet but the following suggests how to do it manually.

1. On the accounts tab insert a row in the table
2. Fill in all fields (notes is optional). Usually, the account name is used for the actl_source
3. Create the rows on the balances table as follows:
      1. Unhide all columns and sort by account name
      1. Insert 9 new rows
      1. Copy the 9 value types into column B 
      1. Put the account name in all 9 of the new rows in the AcctName field
      1. Construct the Key (concatenate the values of ValType and AcctName) - it needs to be be values not a formula
      1. Copy actual formulas and forecast formulas from another account

## Rename an account

It turns out to be useful to have an account naming convention.  The convention is 
	*type - owner - firm*
where type is 401K, 529, BKG, ESP, HSA, IRA, IRA Roth, MUT, BND<br/>and owner is JNT or the owner's initials.

Notes 

- BND is for - gov't bonds where TRY is for treasury - direct

Here's what has to be done to rename an account.

1. The account name can be changed in Moneydance using the Tools -> Accounts menu.

2. It must be changed in the spreadsheet at the following locations
      1. tbl_accounts - it occurs in the A column and may occur in the G column
      1. tbl_balances - it occurs in the AcctName and Key columns
3. Depending on the account it may occur in the following location
      1. tbl_retir, 
      1. tbl_retir_parms
      1. tbl_invest_actl

4. The following should be refreshed: tbl_transfers_actl by running the procedure

## Accounting

The computation of balances depends on the ability to determine the changes to the accounts.  

### Investments

The performance report provides opening and closing balances, income, gains and something called "Return Amount". It does not indicate unrealized gains per se.  The "Return Amount" is essentially a plug to get to the ending balance.  Note - income needs to be marked MiscInc (not transfer to the income category)

Gains are essentially realized gains. Fees for purchases and/or sales of securities are included as part of the cost basis.  Other fees, that occur outside of the purchase or sale transaction are not included - such things as commissions, other account fees, and others. 

The other fees are rolled into the plug field (Return Amount), along with unrealized gains. It is better to include them in the Gains and therefore the 'Rlz Int/Gn' value in the spreadsheet. Thus when an account is closed, there will be no unrealized gains. 

To do this the investment fees need two categories.  Investing:Action Fees, Investing:Account Fees.  Only the account fee is selected in the Investment IandE report.  This allows the loading of investment actuals to add the account fees to the gains.  It also means that the transaction fees are not used to forecast future fees.  This is reasonable since they are by nature not asset based and the forecast method uses percentage of assets.

### Other Assets

The "Other Asset" account has several sub-accounts, including receivables from a few parties.  The method of determining the transfers depends is to use the `transfers-to-fcast` memorized report.  Some of the sub-accounts in Other Asset have transactions using expense categories.  To support this the memorized report includes all expenses in the criteria.  This correctly gathers the amounts such as depreciation for cars and payments made against some expense category (on our behalf).  The set of a target accounts configured in this report includes all investment, loan, asset and liability accounts.   Whenever there is a transfer between these accounts, this method essentially cancels out that values, which can lead to wrong balances.  Such transactions should be routed throught the `Passthru` bank account to avoid this problem.

