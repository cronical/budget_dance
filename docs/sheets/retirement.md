# retirement

Plans out income streams and post-retirement medical expenses.  This affects both the balances and the iande tabs.

## Retirement Income Plan

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
|Item|A computed key, composed of type, whose, and firm.|
|Who|Initials of who owns this account or JNT for joint. Normally hidden.|
|Type|See [conventions](../spreadsheet.md#conventions). Normally hidden.|
|Firm|The firm holding the account. Normally hidden.|
|Election|A code for the distribution election on this item.|
|Start Date|Expected start date for the distribution or expense|
|Anny Dur Yrs|If an annuity is elected, how many years should it run.|
|Anny Rate|The rate used for the annuity|
|Yearly|For non-annuity ongoing values (pensions), yearly amount.|

### Election Codes

|Code|Description|
|:--|:--|
|ANN|Annuity - Creates an annuity stream based on the prior year's end balance, using the `Start Date`, `Anny Dur Yrs`,	`Anny Rate` fields. Currently prorates the start by month, but does not do the same for the last period. 
|RMD-1|This determines the required minimum distribution for inherited IRAs|
|ROLLOVER|Also treated as a annuity, so the only natural duration is one year. |

The following correspond to the headings on the pensions facts table. These are used to look up the data there.  The annual amount is then placed in the Yearly column and it is applied to future years.

- Single
- EE50
- Spouse50
- EE75
- Spouse75
- EE100
- Spouse100
- Lump
- 10 year certain

For items that start with SS, the codes are looked up in the Social Security table. The codes consist of the initials of the person and the year portion of the age when starting to receive social security.

### How to model a rollover from a 401K to an IRA

1. On the retirement table:
    1. set ROLLOVER as the code
    1. set `Start Date` as January 1st of the rollover year
    1. set `Anny Dur Yrs` as 1
    1. set `Anny Rate` as the precise value of the `Mkt Gn Rate` on the balances tab. Five or six significant digits seems to eliminate residual balances.
    1. note the exact amount to be rolled over
1. To prevent this from being taxed:
    1. Ensure additional rows are created on the `iande` table, in the distributions area using the `hier_insert_paths` key. In the following example the second set of rows are created under `Rollover`.
![example](../images/tgt/rollover_1.png)
    1. Populate these rows with a forecast formula such as:
      ```yaml
      =-SUM(FILTER(INDIRECT("tbl_retir_vals["&this_col_name()&"]"),(tbl_retir_vals[Item]=TRIM([@Account]))*(tbl_retir_vals[Election]="ROLLOVER"),0))
      ```
    3. This will produce a total line on the `iande` table that nets out the rollover.  Assuming taxes references that, the result is that the rollover won't be taxed.
![example](../images/tgt/rollover_2.png)
1. Enter the amount rolled over into the `transfers_plan` table as a transfer from bank accounts to the target account.
1. Use the aux table to compute the net changes to the target IRA account.   
    1. User the hier_insert_paths key to insert something like
    ![example](../images/tgt/rollover_3.png)
    1. Set the formulas for withdraws to pull from retirement
    ```
    =-XLOOKUP(INDEX(TEXTSPLIT([@Key],":"),1),tbl_retir_vals[Item],INDIRECT("tbl_retir_vals["&this_col_name()&"]"))
    ```
    1. Set the formula for rollovers to pull from the `transfers_plan` (assume only positive rollovers):
    ```
    =SUM(FILTER(tbl_transfers_plan[Amount],(tbl_transfers_plan[To_Account]=INDEX(TEXTSPLIT([@Key],":"),1))*(tbl_transfers_plan[Y_Year]=this_col_name()),0))
    ```

1. Configure the IRA accounts on balances to pull the `Add/Wdraw` line from `aux`.

    ```
    =XLOOKUP(TRIM([@AcctName])&" - TOTAL",tbl_aux[Key],INDIRECT("tbl_aux["&this_col_name()&"]"))
    ```

1. Extract the retirement values and the transfers plan data 

    ```bash
    (.venv) george@GeorgesacStudio budget % dance/util/extract_table.py -t tbl_retir_vals -w data/test_wb.xlsm
    2023-07-19 20:02:21,229 - extract_table - INFO - Source workbook is data/test_wb.xlsm
    2023-07-19 20:02:21,560 - extract_table - INFO - Wrote to data/retire_template.tsv
    (.venv) george@GeorgesacStudio budget % dance/util/extract_table.py -t tbl_transfers_plan -w data/test_wb.xlsm
    2023-07-19 20:02:34,639 - extract_table - INFO - Source workbook is data/test_wb.xlsm
    2023-07-19 20:02:34,961 - extract_table - INFO - Wrote to data/transfers_plan.json
    ```

1. Rerun the build

## Retirement Medical

Retirement medical values are modeled here. Medicare Part B and Part D have their own rows on this table, so that the variable cost can be modeled (based on year -2 income). The items with type=PKG get their values as the sum of the rows in `tbl_mcare_opt` with the matching package.

The values from this table get carried into the forecast in `tbl_iande`.

### Fields

- Item is manually constructed from Who, Type and Firm.  
- Package - refers to a set of items on the `tbl_mcare_opt` table. The logic sums these, applies the start and end dates and places the value in the years.
- Spare_x - are there just to keep the years aligned with the income plan table.
- Start Date of the month when this line applies
- End Date (if given) ends the cost after this month.

### Setup

Setup sources this from: data/retire_medical_template.tsv
To refresh that file: edit it.
