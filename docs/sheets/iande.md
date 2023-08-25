# iande

This is for income and expenses. There is one table, which uses the "folding" approach.  The folds follow the chart of accounts, with some modifications to support cash flow.

## iande

This is both actuals and forecast.  

It has two leading columns then the actual and forecast years:

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
|Key|The full multi-level category name, anchored as Income or Expense, such as `Expenses:T:Income Tax:Current Yr:Fed:Est pmts`. This column is normally hidden.|
|Account|The last portion of the key, indented by two spaces for each level|

The levels are grouped using Excel's grouping, so they can be expanded or collapsed.

## Cash Flow data

The native high level qualifiers coming from Moneydance Income and Expense.  Under that are I,T, and X, which function identify income, taxes and expenses.  In order to accomodate cash flow items two new codes are introduced. J for money flowing in (such as a distribution from an IRA) and Y for money flowing out (such as payroll deduction for 401K or dividends reinvested).

By accounting for all these flows, the bottom line will be zero for actuals.  For forecasts, the bottom line indicates the amount that can be put in or taken out of bank accounts.

These are configured under the `data:hier_insert_paths` key.

## Reforecasts

It is possible to reforecast selected rows for the current (first forecast) year.  This is done on the `current` tab, which has the same rows as `iande`. When the values are posted to this tab, they are marked with a comment.

The mechanism is described [here](../operations.md#year-to-date-and-reprojection).

