# current

This sheet takes the year to date data from Moneydance and allows the user to apply a factor to reproject the current year.  There is one table.

## current

Titled, YTD and Reprojection, the tbl_current has three leading columns; the first two are hidden.

The reprojection formula is 

`Year = (YTD * Factor) + Add`


For instance, use 1 and 0 if the year-to-date value is final.  

If both Factor and Add are blank it means the value won't be transferred to `iande`, so the modeled value will be retained.

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
|Key|The full multi-level category name, anchored as Income or Expense, such as `Expenses:T:Income Tax:Current Yr:Fed:Est pmts`.|
|is_leaf|1 if the category is a leaf in the category tree, otherwise 0.  Used to pull only leaves (not subtotals) into iande.|
|Account|The last portion of the key, indented by two spaces for each level|
|YTD|The year to data data which has been imported. The column name is replaced by the as of date in the form Yyyyymmdd|
|Factor|A number used in the formula.|
|Add|A number used in the formula.|
|Year|The result of the formula, or blank if not re-projected.|

The rows are handled like iande with groups, totals and hierarchical inserts.

The mechanism is described [here](../python.md#year-to-date-and-reprojection).

Currently the distributions (Income:J) and cashflow (Expenses:Y) are not imported but if used, they are carried to storage and to iande.