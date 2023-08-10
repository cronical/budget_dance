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

## Reference to actual data

The current design is probably overcomplicated in that `iande` pulls in values from `iande_actl`, on the theory that it is `iande_actl` that would be updated and it was desirable not to alter the formulas for forecast.  As the concept shifted from initial generation to frequent re-generation, this will probably be deprecated.  In the future the `iande_actl` will go away and the actual columns here will hold actual values directly.

### Current arrangement

This tab is seeded with the original iande-actl data.   But it is expected that over time the rows will change.  For instance, if we later drop the first few years, we will find that some of the rows no longer come over from Moneydance.  On the other hand, we may add rows in Moneydance.  It is also possible that we may want to re-organize or rename the rows.  Take deleted rows first.

1. Deleted Rows - The python script that loads the latest from Moneydance performs a check before executing the load.  It requires that any row that contains data or a fomula in the forecast era exist in the fresh import from Moneydance, when seeding the iande data.
2. New rows - The new rows will be added into the `tbl_iande-actl` table but the `tbl_iande` won't know about them, possibly yielding totals that don't match.  At this point its up to the operator to make any needed adjustments to `tbl_iande` so that it's consistent with the actuals feed. Note - if new subcategories are created: then its best to insert them on `tbl_iande` so that what used to be a leaf node now has no data (its just a heading), copy the fixed values to the new rows and ensure the subtotals are proper for non-fixed (forecast values). Note: the report filters out categories that do not have any actuals.  In order to create forecasts for these, go ahead and create the desired rows in Moneydance and manually construct the rows in `tbl_iande`.
3. Re-arrangement and renaming - At this point its up to the operator to make any needed adjustments to `tbl_iande` so that it's consistent with the actuals feed.

The net of this is that except during periods of change, the rows of the iande tab and the rows of the iande-actl tab form the same set.  We don't require these to be in the same order.

