# retirement

Plans out income streams and post-retirement medical expenses.  This affects both the balances and the iande tabs.

## Retirement Income Plan

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
|Item|A key, composed of type, whose, and firm, separated by space-hypen-space like `401K - GBD - XXX`|
|Who|Initials of who owns this account or JNT for joint. This is split from Item at build time and stored.|
|Type|See [conventions](../workbook.md#conventions). This is split from Item at build time and stored.|
|Firm|The firm holding the account. This is split from Item at build time and stored.|
|Election|A code for the distribution election on this item.|
|Start Date|Expected start date for the distribution or expense|
|Anny Dur Yrs|If an annuity is elected, how many years should it run.|
|Anny Rate|The rate used for the annuity|
|Yearly|For non-annuity ongoing values (pensions), yearly amount.|

### Election Codes

|Code|Description|
|:--|:--|
|ANN|Annuity - Creates an annuity stream based on the prior year's end balance, using the `Start Date`, `Anny Dur Yrs`,	`Anny Rate` fields. Currently prorates the start by month, but does not do the same for the last period. 
|RMD-BEN-YYYY|This determines the required minimum distribution for IRAs inherited as a beneficiary. The YYYY is replaced with the year of death of the former owner|
|RMD-SPOUSE|This determines the required minimum distribution for IRAs inherited as a spouse.|
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

### Data Source

These values are sourced from `data/retir_template.tsv`.  If the values are changed, the template can be re-written using the extract_table utility.

## Retirement Medical

Retirement medical values are modeled here. Medicare Part B and Part D have their own rows on this table, so that the variable cost can be modeled (based on income 2 years back). The items with type=PKG get their values as the sum of the rows in `tbl_mcare_opt` with the matching package.

The values from this table get carried into the forecast in `tbl_iande`.

### Fields

- Item is manually constructed from Who, Type and Firm.  
- Package - refers to a set of items on the `tbl_mcare_opt` table. The logic sums these, applies the start and end dates and places the value in the years.
- Spare_x - are there just to keep the years aligned with the income plan table.
- Start Date of the month when this line applies
- End Date (if given) ends the cost after this month.

### Data Source

These values are sourced from `data/retire_medical_template.tsv`.  If the values are changed, the template can be re-written using the extract_table utility.
