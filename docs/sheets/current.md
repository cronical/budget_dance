# current

This sheet takes the year to date data from Moneydance and allows the user to apply a factor to reproject the current year.

## ytd

Like `iande` it has two leading columns.

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
|Key|The full multi-level category name, anchored as Income or Expense, such as `Expenses:T:Income Tax:Current Yr:Fed:Est pmts`. This column is normally hidden.|
|Account|The last portion of the key, indented by two spaces for each level|
|YTD|The year to data data which has been imported. The column name is replaced by the as of date in the form Yyyyymmdd|
|Factor|A number by which to multiply the year to date value to get the full year.  For instance use 1 if the year to date value is final.  A blank means the value won't be transferred to `iande`, so the modeled value will be retained.|
|Year|The product of YTD and Factor, or blank if not re-projected.|

The rows are handled like iande with groups, totals and hierarchical inserts.