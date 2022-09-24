# Design and use of fcast.xlsm

## Purpose

This system extends the family's historical financials into the future.  It allows for planning for income/expenses as well as financial moves between accounts.   It has a tax calculator (which is far from general, but works for us). 

## General set up

The system uses a set of Excel tables, which are distributed over a set of worksheets. 
Many of the tables represent time series where the time is based on years.  The data elements are typically financial values assoicated with a year.  For instance, the balances table tracks how balances change year by year.

The time sequence columns are labeled with 'Y' + year.  Other columns are labeled with appropriate short column labels.  The meaning of the column data depends on the state of the system.  To the left of some point, data is considered actual, while to the right it is forecast.

Use of Visual Basic (macros) allows for calculations to be done in a more readable manner.  However there is a downside.  This is that Excel cannot use its dependency trees to know what need to occur when the macros reference or update done with this method.  So far I have not turned on the use of the application volitile method, as there is significant overhead, possibly causing slow performance. There is a macro, currently called calc_retir(), to perform the re-calcuations in the correct order. 

External access to the spreadsheet is used. Mostly these are programs to transfer Moneydance actual data into the Workbook.  This is done via Python using the openxlpy library.  These files are in the `dance` subfolder.

One of these Python files, `util/index_tables.py` enumerates and indexs the tables (something oddly missing in Excel due to the fact that it is worksheet oriented). The index is stored on the utility worksheet.

## Worksheets

### accounts

This worksheet lists the tracked accounts and their attributes. Some of these accounts are real accounts at financial institutions.  Others summarize sets of assets or liabilities. One account is designated as the sweep account.

The attributes are:

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| Type            | A=Asset, B=Bank, C=Credit Cards, I=Investment, L=Liability, N=Loans |
| * Income Txbl     | 0 if sheltered, 1 if normal taxes|
| Active          | 0 if inactive, 1 if active                                   |
| *Rlz share       | between 0 and 1 - factor to apply to income to categorize as realized in forecasts |
| * Unrlz share     | same as above, but for unrealized.  These should add to 1.   |
| actl_source     | The line name where to find the actual add/wdraw amount      |
| actl_source_tab | The table name where to find the actual add/wdraw amount     |
| fcst_source     | The line name where to find the forecast add/wdraw amount    |
| fcst_source_tab | The table name where to find the forecast add/wdraw amount   |
| notes           | Place to indicate special things about the account           |

* under revision

### balances

The following fields are looked up from the account page: Type, Income Txbl, and Active.

This table has six rows for each account.  

| ValType     | Formula                                                      |
| ----------- | ------------------------------------------------------------ |
| * Rate        | Used to forecast gains, which are split by the indicators on the account rows.  Computed for historical rows. |
| Start Bal   | Previous year's end balance                                  |
| Add/Wdraw   | Either manual, or some rows will have formulas               |
| * Rlz Int/Gn  | start * rate * split                                         |
| Unrlz Gn/Ls | start * rate * split                                         |
| End Bal     | Adds the start balance to each of the other change categories. |

The calculations are designed to work even if the rows are filtered or sorted.  To restore to the natural sort order sort by AcctName then ValType (using a custom sort order that is defined)

### Investment Income and Expenses

From an accounting perspective the `Rlz Int/Gn` consists of short and long term gains combined with income.
The realized gains consist of Interest, Dividends and Capital Gains
Accounts are sheltered or not. For non sheltered accounts additional breakdown is needed.  
Dividends - taxable and tax exempt  
Interest - taxable and tax exempt  
Capital Gains - short and long term  

Dividends are further broken down into qualified and non qualified, but this is only reported after the year end, so we don't track it on the iande tab.  This means that all dividends are considered non-qualified in forecast years at least by default.

Alignment is needed between forecast balances and forecast income so that the number balance.
To generate approximate tax forecasts is needed to have the investment income types broken out.  

CapGn:Mut LT  
CapGn:Mut ST  
CapGn:Shelt  
Div:Reg  
Div:Shelt  
Div:Tax-exempt  
Int:Reg  
Int:Shelt  
Int:Tax-exempt  

See [Appendix](./appendix.md#changes-to-existing-categories)

#### Reinvestment

Prior versions assumed all income was re-invested.  Proper modeling will also require consideration of re-investment policies. This will be modeled as a re-investment rate at the account level.

#### Column changes in Accounts
Add: 
- Re-investment Rate - the amount re-invested, the remainder is transfered to the primary bank (new item in General State)
Remove: 
- Rlz share
- Unrlz share

#### Tax exemption

Tax exemption is in reality further broken down into federal and state.  In theory it should be implemented on a per security basis.  But it only matters for taxation so it is handled by custome lines on the taxes sheet by year.

#### Balances

Rows in balances are mostly the same. The plethora of income types are handed on a [new table](#table-iande-invest-work). 

The rlz Int/Gn line is currently derived from the investment performance report. This report does not break out the income types.  If the accounting is done properly then the breakout for a particular investment account can be achieved via an income/expense report that selects that account. The value of the performance report 'Income' column total is equal to the value of the Investment Income report line Income - TOTAL.

Neither report provides a breakout of income by div/int/capgn by account.

For actual periods, it is possible to see if these totals balance. For forecast periods the values could be derived from rates or otherwise estimated on a per account basis, then summed one way for the balances and another way for the iande tab.  A new table could support this or it could be done directly on the balances table.

Example: Brokerage with muni funds

Div Pct/Val  0  0  
Int Pct/Val  3.77%  16,724  
CapGn Pct/val -0.25%  -1101  
UnRlz Pct/val -3.97% -16871

The `invest-actl` table field `Gains` represent capital changes due to sales, only.  This value comes from the investment performance report.

This is different than those amounts reported by mutual funds as capital gains distributions - essentially a form of dividend but marked as LT or ST for tax purposes. This value comes from dividend transactions in the account and is exposed via the I and E report.  

#### Table iande invest work

The set of lines that represent income and expenses for each account is added to a new table:`tbl_invest_iande_actl`.  

The actuals derive from a Moneydance report: Investment IandE, which is a configured Transaction Filter that selects just the investment income and expense lines for all accounts. It should select dates over the years that are actuals.  The result is saved into `invest-iande.tsv`.  

The values are summarized by investment accounts for each of the categories.  These become the numerators of the actual rates experience for each category for each account.  The denominator is the opening balance of the account. Its imperfect for accounts where money is moved in or out during the year, but it is adequate for its use of setting default rates for forecast years.

The summarization is done on they Python side at load time.  The ratios are calculated in the spreadsheet. Rates are rounded to 1 basis point (.01%).  The rolling average of the previous periods is used to carry the rates into the forecast period.

The balances table is also modified to replace the `Rlzd Int/Gn` with the same lines as needed for each account. This allows the `iande` forecast for these lines to be calculated as the sum across all accounts for the line for forecast periods.  For actual periods those values will derive directly from the Moneydance report (and they had better be the same).

The existing rate line no longer has the same meaning or usage.  It will be used only for unrealized gains and as such will be renamed to `Mkt Gn Rate`.

New rows will exist for each type of income or expense according to a naming convention, which aligns with the Moneydance category names, to facilitate mapping.  These rows will be paired with other rows with ` rate` appended to hold the ratio to the `start bal` in the case of actuals.  These rate  rows that are extended into the forecast period where they are used to compute forecasts for each of the income/expense types.




### invest-actl

The Python program `invest-actl-load.py` gets the master list of investment accounts from `fcast.xlsm`.  It then reads the `data/invst_*.tsv` files and computes the net flows for each account by year.

The MoneyDance Investment Performance report is named `invest-p-YYYY.tsv`. There is one for each actual year. The program reads these as well.

It ends up with 3 rows of actuals for each investment like:

| ValType     | AcctName          | Y1 | Y2    | Y...   | Yn    |
| ----------- | ----------------- | ------ | -------- | ------- | -------- |
| Add/Wdraw   | 401K | 0   | 0        | 0       | 0        |
| Rlz Int/Gn  | 401K | 0   | 0        | 0       | 0        |
| Unrlz Gn/Ls | 401K | 0   | 0        | 0       | 0        |

This can be used to look up the actuals on the balances tab. The visual basic function `gain` references the realized and unrealized gain lines for actuals. the visual basic function `add_wdraw` likewise references the first line.

### transfers-actl

Gathers the transfers to and from all accounts coming from or going to banks or credit cards.  This also shows the transfers to and from bank and credit card accounts.  The bank and credit card transfers are derived another way and are also included on this tab.

If there are transfers between these accounts, then they should pass through a bank account in order to be captured here.  That is the purpose of the pseudo bank account 'Passthru' and its sub-accounts in Moneydance.

This tab is loaded by `transfers-actl-load.py` from these sources:

1. A copy of the output of moneydance transfer report stored under `budget/data`.  
2. The method used is the difference of progressive balances.  The balances are generated by the `Account Balances` report selecting only banks and credit cards.  This is done for each year.  The tab-separated files are stored under `budget/data` as `bank-bal-YYYY`. 
3. A third method is planned which will ensure that all accounts have rows - even those with zero transfers.

### iande-actl

This is Income and Expense actuals as it comes from Moneydance `Income & Expense by Year` report.  A key is constructed which includes the hierarchy.  That occurs in the A column. The summary rows are replaced by formulas as part of the import process.  These can be copied into future years. The column headings are of the Y+year style to facilitate lookups.  

This data is loaded from `data/iande.tsv` with the program  `iande-actl-load.py` 

#### IRA-Txbl-Distr
This line is needed to handle the accounting difficulty that arises with IRA distributions when the source account is in Moneydance (see note).  The gross amount is taxable and thus needs to be included in the tax calculation.  However, the tax amounts go to the state and federal expense lines and the net goes to the receiving bank.  There is no place to declare income.

The solution allows a uniform way of handling the data (at the cost of a bit of special handling). 

The solution uses a Moneydance tag, `IRA-Txbl-Distr` on those transactions.  This involves editing the transactions that are downloaded from the financial institution to add in the tag. This needs to be done in the Bank Register view not the Register view.  The tags field is only shown in the Bank Register view. 

This data is exported from Moneydance via the `IRA-Distr` report, and saved in the `data/IRA-Distr.tsv`file. It is then imported via special handling in `iande_actl_load`, which calls the `ira_distr_summary()` function and merges the data into `IRA-Txbl-Distr` line on the iande_actl table.  From there it flows to the `iande` tab and then to the `taxes` tab.  The value in `iande_actl` may have values for some years (if the distribution comes from an account not tracked by Moneydance.  This can happen with an inherited IRA).

### iande-map

(Planned) assists with mapping actuals to rows in iande. See item 3 under iande.

### iande

This is for income and expenses. This is both actuals and forecast.  This tab is seeded with the original iande-actl data.   But it is expected that over time the rows will change.  For instance, if we later drop the first few years, we will find that some of the rows no longer come over from Moneydance.  On the other hand, we may add rows in Moneydance.  It is also possible that we may want to re-organize or rename the rows.  Take deleted rows first.

1. Deleted Rows - The python script that loads the latest from Moneydance performs a check before executing the load.  It requires that any row that contains data or a fomula in the forecast era exist in the fresh import from Moneydance, when seeding the iande data.
2. New rows - The new rows will be added into the `tbl_iande-actl` table but the `tbl_iande` won't know about them, possibly yielding totals that don't match.  At this point its up to the operator to make any needed adjustments to `tbl_iande` so that it's consistent with the actuals feed. Note - if new subcategories are created: then its best to insert them on `tbl_iande` so that what used to be a leaf node now has no data (its just a heading), copy the fixed values to the new rows and ensure the subtotals are proper for non-fixed (forecast values). Note: the report filters out categories that do not have any actuals.  In order to create forecasts for these, go ahead and create the desired rows in Moneydance and manually construct the rows in `tbl_iande`.
3. Re-arrangement and renaming - At this point its up to the operator to make any needed adjustments to `tbl_iande` so that it's consistent with the actuals feed.

The net of this is that except during periods of change, the rows of the iande tab and the rows of the iande-actl tab form the same set.  We don't require these to be in the same order.

### aux
This is a set of rows needed to establish forecasts in some cases.  The rows may be input or calculated.  The need arises for aux data and calcs, for instance, in handling 401K accounts, where the EE contribution is tax deductable but is only part of the amount for add/wdraw at the balance level.  That value plus the pre-tax deductions amounts from the paychecks need to be summed to produce the W2 exclusions.  This is the place where those calcs happen. 

The calculations are flexible, but they often use the form of looking up a value and multiplying it by the value in the sign field.  Mostly the sign field is used to change or retain the sign, but it can be used to apply a scalar value such as a tax rate. 

The following style is used to allow the table to be relocated and makes the formula apparent from the values in cells.

```=@get_val([@Source],[@[Source Table]],this_col_name())*[@Sign]```

this_col_name is a VBA function that gets the current column table name.

The field 'Accum_by' is intended to allow summations using the `accum` function.  If a value needs more than one tag, create another row with the same data and a different tag.  An example of this 401K deductions, which generate W2 exclusions on one hand and the need to deposit amounts into the 401K account.


### capgn

This is for the purposes of 

1. estimating taxes for the current and prior year until tax statements arrive
2. reconciling between balances (which includes realized capital gains) and income (which only includes capital gains arising as dividends, but not from sales of securities).

### taxes

This computes Federal and State income taxes. It requires the data from the tables tab.  For actuals it pulls data mostly from iande-actl.  A few income fields need to come from tax documents. 

### tax-est

This helps figure if estimated taxes are needed or if W4 filings need to be made.

### tables

A table of state tax information, tax tables, Medicare Part B premiums, inflation, required minimum distribution tables, and a general state mangement table.

#### Federal tax tables

These use the subtraction method in IRS pub detailed here: https://www.irs.gov/pub/irs-pdf/i1040gi.pdf.  This takes 6 rows and 4 columns per year.  These are organized in a single table.  A VBA macro is used to select the right values for use on the `taxes` tab. 

The prgram `bracket_fix.py` computes the numbers for the subtraction table based on a csv file which is shows the values using the additive method. Not sure where I found that file, most recently, I recreated the format.  Kind of painful.  May be best to wait for the 1040 Instructions to be published each year. (Or find a reliable source)

#### state taxes
This compiles facts about various states for the purpose of considering relocation. Can be referenced in the tax calcs. Source: https://www.kiplinger.com/tool/retirement/T055-S001-state-by-state-guide-to-taxes-on-retirees/index.php

#### Part B Premium

Values to select the premium given modified AGI and year.

#### inflation

3 columns about 75 rows
#### RMD
Table III is for normal plans.  Table I is for beneficiaries (inherited IRA).

#### State management

Currently this has only one value, the first forecast year.

### retirement

Plans out income streams and post-retirement medical expenses.  This affects both the balances and the iande tabs.

Retirement medical is modeled here.   Deductibles and copays are in 'other'. These values are posted as totals in the premium lines of IANDE and are meant to represent all net medical expenses.

### retireparms

#### parameters to drive the retirement tab
To make the calculations more understandable some are done on this table. For instance, the months column is input data, which is used to offset the birthday of the account owner to yield a start date.

#### pension options

Facts about pensions used by retirement sheet.  

### hsa

A page with a section for each HSA account.

### manual_actl

A number of entries are needed to determine taxes.  When easiest, these are input on this table: `tbl_manual_actl`. A Moneydance report `W2-exclusions` extracts the amounts that can be excluded from the W2s.  This relies on the Pre-tax and pre-tax tags. These should be input manually.

Computes the actual 401K contributions to post to the iande tab.

## functions

There are Visual Basic for Applications functions in this worksheet.  There are some complex dependencies.  Currently, in some cases it is necessary to run `calc_retir` in order to complete the calculations. 

### tables

The get_val routine requires the use of worksheet tables.  This allows the tables to have their own column names and for the values to be located.  Tables are located on worksheets.  So that we don't have to care about that an index of tables is created in the 'utility' worksheet.  This itself is a table and it is created by a Python program `index-tables.py`.

### conventions

All table names begin with `tbl_`.
Always use lowercase except for acronyms 
Use underscores between words
Use std abbreviations: actual=actl; balances=bals; investments=invest; retirement=retir; annuity=anny;duration=dur;pension=pens; value or valuation = val;parameters=parms

### ranges
The use of named ranges is minimized due to the use of structured tables. The following are the ones remaining of the initial plan.  These will changes as needed.

HSA_g_actl
HSA_g_years
infl_data
xfer_to_invest
xfer_to_non_invest
xfer_to_other


