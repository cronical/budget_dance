# Data from Moneydance

## Python Environment
In the terminal change the current directory to the root of the repository.
Use the following command to active the virtual environment: `source .venv/bin/activate`

## Copy Income and Expense from Moneydance

1. In Moneydance run `Income & Expense by Year`
2. Save as `data/iande.tsv` 
3. Close spreadsheet and run the program  `iande-actl-load.py` 
4. Ensure that the formulas on the year are set to `getval...`
5. Check that income, tax and expense totals match to report: 
   * start at level 3 and drill down to find problems.
   * IRA distributions are problematic (see note IRA-Txbl-Distr - line)
   * If there are new categories - you will need to insert a line

## First pass on the taxes 

The first pass does not rely on the tax forms, those come later - basically the bits that are not accounted for are entered into the manual_actl tab.

1. Check W2 exclusions on aux
2. Change the column for the year to use the actuals
3. Carefully check the progression of the logic

## Copy transfers data from Moneydance

1. Run report in Moneydance (currently called Transfers-to-fcast.
2. Press Save button and choose Tab delimited and save as `data/transfers.tsv`
3. (If a year has been completed run the Bank balance export procedure)
4. If `fcast.xlsm` is open, save your work and close the file.
5. Open a terminal window at the project root.
6. Run `python transfers_actl_load.py`
7. Re-open the spreadsheet and save it to force balances to recalc and be stored.

## Bank balance export procedure

The method used is the difference of progressive balances.  This is done for each year.  

1. In Moneydance run the `Account Balances` report selecting only banks and credit cards.  
2. Save the file as tab-separated under `budget/data` as `bank-bal-YYYY`.
3. These files are consumed by the `transfers_actl_load.py` routine.

## Investment actuals

The Tranfers to Investment Accounts by Year report is saved as `invest_x.tsv`. The Investment Performance report for each year is saved under `invest-p-yyyy.tsv` for each year. These are processed by `invest_actl_load.py`. At each year end:

1. Run `Tranfers to Investment Accounts by Year` and save as `invest_x.tsv`
2. Run `Investment Performance` report for the year and save under `invest-p-yyyy.tsv`
3. If `fcast.xlsm` is open, save your work and close the file.
5. Open a terminal window at the project root.
6. Run `invest_actl_load.py`
7. Re-open the spreadsheet and save it to force balances to recalc and be stored.

## Validate balances for a year

The routine `balance_check.py` is available to see how the values from the `Account Balances` report in Moneydance match to those in `fcast.xlsm`. 

1. In Moneydance run the `Account Balances` report selecting all accounts. 
2. Save the report  under the names: `data/yyyy Account Balances.tsv`.
3. If the year has rolled over in the spreadsheet
  - change first_forecast_year in on the tables worksheet.
3. In a terminal window set current directory to the project root and run `balance_check.py yyyy` where yyyy is the year to check.  You should get a listing that shows the exact matches and the accounts that don't match (and how much they are off).



## Add an account
1. On the accounts tab insert a row in the table
2. Fill in all fields (notes is optional). Usually, the account name is used for the actl_source
3. Create the rows on the balances table

|      | Steps                                                        |
| ---- | ------------------------------------------------------------ |
| 1    | Unhide all columns and sort by account name                  |
| 2    | Insert 6 new rows.  Put the account name in the first row of the AcctName field. |
| 3    | Copy down columns A, D, E, F from another account.           |
| 4    | Copy the 6 value types into column B                         |
| 5    | Insert 6 copies of the new account name for each account in  column c |
| 6    | Copy formulas into 1st active year                           |
| 7    | Set the opening balance                                      |
| 8    | When satisfied with actuals, copy formulas into 1st forecast period |

## Rename an account

It turns out to be useful to have an account naming convention.  The convention is 
	*type - owner - firm*
where type is 401K, 529, BKG, ESP, HSA, IRA, IRA Roth, MUT, BND<br/>and owner is JNT or the owner's initials.

Notes 

- BND is for - gov't bonds where TRY is for treasury - direct

Here's what has to be done to rename an account.

1. The account name can be changed in Moneydance using the Tools -> Accounts menu.

2. It must be changed in fcst.xlsm at the following locations
   1. tbl_accounts - it occurs in the A column and may occur in the G column
   2. tbl_balances
3. Depending on the account it may occur in the following location
   1. tbl_retir, 
   2. tbl_retir_parms
4. The following should be refreshed: tbl_transfers_actl by running the procedure

## Accounting

The computation of balances depends on the ability to determine the changes to the accounts.  The "Other Asset" account has several sub-accounts, including receivables from a few parties.  The method of determining the transfers depends is to use the `transfers-to-fcast` memorized report.  Some of the sub-accounts in Other Asset have transactions using expense categories.  To support this the memorized report includes all expenses in the criteria.  This correctly gathers the amounts such as depreciation for cars and payments made against some expense category (on our behalf).  The set of a target accounts configured in this report includes all investment, loan, asset and liability accounts.   Whenever there is a transfer between these accounts, this method essentially cancels out that values, which can lead to wrong balances.  Such transactions should be routed throught the `Passthru` bank account to avoid this problem.

