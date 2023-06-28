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

## Retirement Medical

Retirement medical values are modeled here. Part B and Part D have their own rows on this table, so that the variable cost can be modeled (based on year -2 income). The items with type=PKG get their values as the sum of the rows in `tbl_mcare_opt` with the matching package.

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
