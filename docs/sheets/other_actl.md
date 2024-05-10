# other_actl

This sheet holds several tables of other actuals.

## Manually input actual items

Mostly values needed for tax calcs. A number of entries are needed to determine taxes.  When easiest, these are input on this table: `tbl_manual_actl`. A Moneydance report `W2-exclusions` provides the amounts that can be excluded from the W2s.  This relies on the Pre-tax and pre-tax tags. These should be input manually.

Computes the actual 401K contributions to post to the iande tab.

## Payroll Savings incl ER contributions

Used by cash flow calcs on IandE.

## Roth contributions

Used in tax calcs.

## 529 plan distributions

Used to populate untaxed income lines in iande.

## IRA distributions

Used to populate `Income:J:Distributions:IRA` lines on iande.

This table is needed to handle the accounting difficulty that arises with IRA distributions.  [See accounting note on IRA-Txbl-Distr](../accounting.md#ira-accounts).

This data is exported from Moneydance via the `IRA-Distr` report, and saved in the `data/IRA-Distr.tsv` file. It is then imported via special handling in `IRA_distr` processes the transactions to create a table `tbl_ira_distr`. The  `Income:J:Distributions:IRA`  line on the `tbl_iande` pulls from that table.  From there it flows to the `taxes` tab.  

## HSA disbursements

Used to populate untaxed income lines in iande.

## Bank transfers to/from selected investments

Used by cash flow calcs on IandE.  These values are similar to the add/wdraw values on `tbl_invest_actl`, but will differ by amounts that flow directly to/from income or expense lines.  An example of that is an inheritance.  If there are no such lines, this table can be omitted and the cash flow calcs derived directly from `tbl_invest_actl`.


