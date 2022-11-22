# Worksheets

## accounts

This worksheet lists the tracked accounts and their attributes. Some of these accounts are real accounts at financial institutions.  Others summarize sets of assets or liabilities. One account is designated as the sweep account.

The attributes are:

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| Account| The name of the account or summay set|
| Type            | A=Asset, B=Bank, C=Credit Cards, I=Investment, L=Liability, N=Loans |
| Income Txbl     | 0 if sheltered, 1 if normal taxes|
| Active          | 0 if inactive, 1 if active                                   |
| No Distr Plan| 0 if there is a distribution plan, 1 otherwise, blank for n/a|
| Near Mkt Rate| Rate to use to override the first forecast year computed rate|
| Rate Cap | Rate used to cap computed rates|
| Reinv Rate| Amount used to initialize the `Reinv Rate` row on the balances table|
| Actl_source     | The line name where to find the actual add/wdraw amount      |
| Actl_source_tab | The table name where to find the actual add/wdraw amount     |
| Fcst_source     | The line name where to find the forecast add/wdraw amount    |
| Fcst_source_tab | The table name where to find the forecast add/wdraw amount   |
| Notes           | Place to indicate special things about the account           |

## balances

The following fields are looked up from the account page: Type, Income Txbl, and Active.

This table has the following rows for each account.  

| ValType     | Formula                                                      |
| ----------- | ------------------------------------------------------------ |
| Mkt Gn Rate | Used to forecast *unrealized* gains.   Computed with `simple_return` for historical rows. |
| Reinv Rate | The part of realized gains that is reinvested each year. Proper modeling also requires consideration of re-investment policies, which are modeled as a re-investment rate per account per year. **TODO**: The remainder is planned to be transfered to the primary bank (new item in General State)|
| Start Bal   | Previous year's end balance                                  |
| Add/Wdraw   | The amount added to the account during the year if positive, or removed if negative. Either manual, or some rows will have formulas               |
| Rlz Int/Gn  | The actual or forecast realized gain, including income and any capital gains or losses.|
| Fees|Account and transaction fees which reduce the value of the account|
| Unrlz Gn/Ls | The unrealized gains due to market changes|
| End Bal     | Adds the start balance to each of the other change categories. |

The calculations are designed to work even if the rows are filtered or sorted.  To restore to the natural sort order sort by AcctName then ValType (using a custom sort order that needs to be defined).

### Rlz Int/Gn line 

For actuals, this value derives from the investment performance report[^2] via the [invest_actl worksheet](#invest-actl).

For forecast periods, the [investment income and expense](#invest_iande_work) values are derived from adjusted extrapolated historical rates on line item basis. These values are then summed one way for the balances and another way for the [iande](#iande) tab.  


## iande

This is for income and expenses. This is both actuals and forecast.  

It has two leading columns then the actual and forecast years:

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
|Key|The full multi-level category name, anchored as Income or Expense, such as `Expenses:T:Income Tax:Current Yr:Fed:Est pmts`. This column is normally hidden.|
|Account|The last portion of the key, indented by two spaces for each level|

The levels are grouped using Excel's grouping, so they can be expanded or collapsed.

This tab is seeded with the original iande-actl data.   But it is expected that over time the rows will change.  For instance, if we later drop the first few years, we will find that some of the rows no longer come over from Moneydance.  On the other hand, we may add rows in Moneydance.  It is also possible that we may want to re-organize or rename the rows.  Take deleted rows first.

1. Deleted Rows - The python script that loads the latest from Moneydance performs a check before executing the load.  It requires that any row that contains data or a fomula in the forecast era exist in the fresh import from Moneydance, when seeding the iande data.
2. New rows - The new rows will be added into the `tbl_iande-actl` table but the `tbl_iande` won't know about them, possibly yielding totals that don't match.  At this point its up to the operator to make any needed adjustments to `tbl_iande` so that it's consistent with the actuals feed. Note - if new subcategories are created: then its best to insert them on `tbl_iande` so that what used to be a leaf node now has no data (its just a heading), copy the fixed values to the new rows and ensure the subtotals are proper for non-fixed (forecast values). Note: the report filters out categories that do not have any actuals.  In order to create forecasts for these, go ahead and create the desired rows in Moneydance and manually construct the rows in `tbl_iande`.
3. Re-arrangement and renaming - At this point its up to the operator to make any needed adjustments to `tbl_iande` so that it's consistent with the actuals feed.

The net of this is that except during periods of change, the rows of the iande tab and the rows of the iande-actl tab form the same set.  We don't require these to be in the same order.

## aux
This is a set of rows needed to establish forecasts in some cases.  The rows may be input or calculated.  The need arises for aux data and calcs, for instance, in handling 401K accounts, where the EE contribution is tax deductable but is only part of the amount for add/wdraw at the balance level.  That value plus the pre-tax deductions amounts from the paychecks need to be summed to produce the W2 exclusions.  This is the place where those calcs happen. 

The calculations are flexible, but they often use the form of looking up a value and multiplying it by the value in the sign field.  Mostly the sign field is used to change or retain the sign, but it can be used to apply a scalar value such as a tax rate. 

The following style is used to allow the table to be relocated and makes the formula apparent from the values in cells.

```=@get_val([@Source],[@[Source Table]],this_col_name())*[@Sign]```

this_col_name is a VBA function that gets the current column table name.

The field 'Accum_by' is intended to allow summations using the `accum` function.  If a value needs more than one tag, create another row with the same data and a different tag.  An example of this 401K deductions, which generate W2 exclusions on one hand and the need to deposit amounts into the 401K account.

## invest_iande_work

This sheet refers to Income and Expenses that relate to investments. The upper left quadrant of the sheet refers to actual values for several categories. These are converted to ratios in the lower left quadrant, so that forecasts can be derived. 

The table consists of
- a set of lines of type `value` that represent income and expenses for each account  
- a matching set of lines with a type of `rate` to hold the ratio to the `start bal`. These are computed in the case of actuals.  The actual rates are extended into the forecast periods where they are used to compute forecasts for each of the income/expense types.

The following categories were devised to support forecasting investment income and taxes[^3].


|	Category	|	Supports	|
|	---	|	---	|
|	CapGn:Mut LT 	|	Long term mutual fund distributions. For taxable accounts - supports tax calc	|
|	CapGn:Mut ST 	|	Long term mutual fund distributions. For taxable accounts - supports tax calc	|
|	CapGn:Sales 	|	Gains or losses from sales in taxable accounts	|
|	CapGn:Shelt:Distr 	|	Mutual fund distributions of any duration in non-taxable accounts	|
|	CapGn:Shelt:Sales 	|	Gains or losses from sales in non-taxable accounts	|
|	Div:Reg 	|	Regular dividends in taxable accounts	|
|	Div:Shelt 	|	Dividends in non-taxable accounts	|
|	Div:Tax-exempt[^1]  	|	Dividends exempt from federal tax in taxable accounts	|
|	Int:Reg 	|	Interest in taxable accounts	|
|	Int:Shelt 	|	Interest in non-taxable accounts	|
|	Int:Tax-exempt 	|	Interest exempt from federal tax in taxable accounts	|

The actuals derive from a Moneydance report: Investment IandE, which is a configured Transaction Filter that selects just the investment income and expense lines for all accounts. It should select dates over the years that are actuals.  The result is saved into `invest-iande.tsv`.  

The values are summarized by investment accounts for each of the categories.  These become the numerators of the actual rates experience for each category for each account.  The denominator is the opening balance of the account. Its imperfect for accounts where money is moved in or out during the year, but it is adequate for its use of setting default rates for forecast years.

The summarization is done on they Python side at load time.  The ratios are calculated in the spreadsheet. Rates are rounded to 1 basis point (.01%).  The rolling average of the previous periods is used to carry the rates into the forecast period. These averages may be modified by the rate cap set on the accounts tab. 

On the balances table the `Rlzd Int/Gn` and `Fees` lines are derived as sums from this table. 

On the `iande` table the forecasts for investment income and expense are also summed up from the values in this table. Forecasts for these lines are calculated as the sum across all accounts for the line for forecast periods.  For actual periods those values will derive directly from the Moneydance [income and expense](#iande) report.

## retirement

Plans out income streams and post-retirement medical expenses.  This affects both the balances and the iande tabs.

Retirement medical are modeled here.   Deductibles and copays are in 'other'. These values are posted as totals in the premium lines of IANDE and are meant to represent all net medical expenses.

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
|Item|A computed key, composed of type, whose, and firm.|
|Who|Initials of who owns this account or JNT for joint. Normally hidden.|
|Type|See [conventions](./fcast.md#conventions). Normally hidden.|
|Firm|The firm holding the account. Normally hidden.|
|Election|A code for the distribution election on this item.|
|Start Date|Expected start date for the distribution or expense|
|Anny Dur Yrs|If an annuity is elected, how many years should it run.|
|Anny Rate|The rate used for the annuity|
|Yearly|For non-annuity ongoing values (pensions), yearly amount.|

## retireparms

### Social Security

This table creates a key for the selected social security election, by which the retirement table can find the value.

### pension facts

Facts about pensions used by retirement sheet.  

## iande-actl

This is Income and Expense actuals as it comes from Moneydance `Income & Expense by Year` report.  A key is constructed which includes the hierarchy.  That occurs in the A column. The summary rows are replaced by formulas as part of the import process.  These can be copied into future years. The column headings are of the Y+year style to facilitate lookups.  

This data is loaded from `data/iande.tsv` with the program  `iande-actl-load.py` 

### IRA-Txbl-Distr
This line is needed to handle the accounting difficulty that arises with IRA distributions when the source account is in Moneydance (see note).  The gross amount is taxable and thus needs to be included in the tax calculation.  However, the tax amounts go to the state and federal expense lines and the net goes to the receiving bank.  There is no place to declare income.

The solution allows a uniform way of handling the data (at the cost of a bit of special handling). 

The solution uses a Moneydance tag, `IRA-Txbl-Distr` on those transactions.  This involves editing the transactions that are downloaded from the financial institution to add in the tag. This needs to be done in the Bank Register view not the Register view.  The tags field is only shown in the Bank Register view. 

This data is exported from Moneydance via the `IRA-Distr` report, and saved in the `data/IRA-Distr.tsv`file. It is then imported via special handling in `IRA_distr` processes the transactions to create a table `tbl_ira_dist`. The  `IRA-Txbl-Distr` line on the `tbl_iande` pulls from that table.  From there it flows to the `taxes` tab.  

The value in `iande_actl` may have values for some years (if the distribution comes from an account not tracked by Moneydance.  This can happen with an inherited IRA). It should match to what is in the `iande` table. If not then the tags probably have not been set correctly.

## other_actl

This sheet holds several tables of other actuals.

### Payroll Savings incl ER contributions

Used by cash flow calcs on IandE.

### 529 plan distributions

Used to populate untaxed income lines in iande.

### IRA distributions

Used to populate retirement income:IRA-Txbl-Distr on iande.

### HSA disbursements

Used to populate untaxed income lines in iande.

### Bank transfers to/from selected investments

Used by cash flow calcs on IandE.

### Manually input actual items

Mostly values needed for tax calcs. A number of entries are needed to determine taxes.  When easiest, these are input on this table: `tbl_manual_actl`. A Moneydance report `W2-exclusions` extracts the amounts that can be excluded from the W2s.  This relies on the Pre-tax and pre-tax tags. These should be input manually.

Computes the actual 401K contributions to post to the iande tab.

## transfers-actl

Gathers the transfers to and from all accounts coming from or going to banks or credit cards.  This also shows the transfers to and from bank and credit card accounts.  The bank and credit card transfers are derived another way and are also included on this tab.

If there are transfers between these accounts, then they should pass through a bank account in order to be captured here.  That is the purpose of the pseudo bank account 'Passthru' and its sub-accounts in Moneydance.

This tab is loaded by `transfers-actl-load.py` from these sources:

1. A copy of the output of moneydance transfer report stored under `budget/data`.  
2. The method used is the difference of progressive balances.  The balances are generated by the `Account Balances` report selecting only banks and credit cards.  This is done for each year.  The tab-separated files are stored under `budget/data` as `bank-bal-YYYY`. 
3. A third method is planned which will ensure that all accounts have rows - even those with zero transfers.


## invest-actl

The Python program `invest-actl-load.py` gets the master list of investment accounts from `fcast.xlsm`.  It then reads the `data/invst_*.tsv` files and computes the net flows for each account by year.

The MoneyDance Investment Performance report is named `invest-p-YYYY.tsv`. There is one for each actual year. The program reads these as well.

It ends up with 5 rows of actuals for each investment.  The values types are:

|ValType|Description|
|---|---|
|Add/Wdraw|Amount moved into or out of account|
|Rlz Int/Gn|Income + Realized Gains|
|Unrlz Gn/Ls|Unrealized gains|
|Income|Interest and Dividends|
|Gains|Realized Gains|

This can be used to look up the actuals on the balances tab. The visual basic function `gain` references the realized and unrealized gain lines for actuals. the visual basic function `add_wdraw` likewise references the first line.


## taxes

This computes Federal and State income taxes. It requires the data from the tables tab.  For actuals it pulls data mostly from iande-actl.  A few income fields need to come from tax documents. 

## capgn

This is for the purposes of 

1. estimating taxes for the current and prior year until tax statements arrive
2. reconciling between balances (which includes realized capital gains) and income (which only includes capital gains arising as dividends, but not from sales of securities).


## tax_tables

A table of state tax information, tax tables, Medicare Part B premiums, inflation, required minimum distribution tables, and a general state mangement table.

### Federal tax tables

These use the subtraction method in IRS pub detailed here: https://www.irs.gov/pub/irs-pdf/i1040gi.pdf.  This takes 6 rows and 4 columns per year.  These are organized in a single table.  A VBA macro is used to select the right values for use on the `taxes` tab. 

The prgram `bracket_fix.py` computes the numbers for the subtraction table based on a csv file which is shows the values using the additive method. Not sure where I found that file, most recently, I recreated the format.  Kind of painful.  May be best to wait for the 1040 Instructions to be published each year. (Or find a reliable source)

### CT Tax Table Married Joint

Multiple years of tax tables for this slice.

### Reqd Min Distr Table I

Table I is for beneficiaries (inherited IRA).

### Uniform Lifetime Table

Also known as Table III, this table is for normal (not inherited) plans.

## gen_tables

A table of state tax information, Medicare Part B premiums, inflation, and a general state mangement table.

### state taxes
This compiles facts about various states for the purpose of considering relocation. Can be referenced in the tax calcs. Source: https://www.kiplinger.com/tool/retirement/T055-S001-state-by-state-guide-to-taxes-on-retirees/index.php


### Part B Premium

Values to select the premium given modified AGI and year. Also includes the part D adjustment.

### inflation

3 columns about 75 rows

### General State

Originally this has only one value, the first forecast year. Other items have been added, so the name is not great.

[^1]: Tax exemption is in reality further broken down into federal and state.  In theory it should be implemented on a per security basis.  But it only matters for taxation so it is handled by custom lines on the taxes sheet by year.

[^2]: This report does not break out the income types.  If the accounting is done properly then the breakout for a particular investment account can be achieved via an income/expense report that selects that account. The value of the performance report 'Income' column total is equal to the value of the Investment Income report line Income - TOTAL.

[^3]: See [Appendix](./appendix.md#changes-to-existing-categories)