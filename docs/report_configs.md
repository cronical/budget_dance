# Report definitions

## Transfers-to-fcast

Source accounts: All bank, All Income, All Credit Card, All Expense
Target accounts: All Load, All Asset, All Liability

Security and Investments are handled via the performance report

## Tranfers to Investment Accounts by Year

This report can be run once for all actual year periods.  It provides transfers in/out of the investment accounts.

Source accounts: All Bank (except Passthru:Pass-IRA-VEC-ML), All Credit Card + certain categories
Target accounts: All Investment

The account Passthru:Pass-IRA-VEC-ML is used to support the strange way the broker handles re-investments.  It has to be excluded from true transfers.

The category I:Untaxed Income:Inherit is used to capture the original income that funded the inherited IRA.

### Certain categories

Two situations have arisen when the use of categories made sense.

1. An inheritance which was transfered directly to an investment account.  In this case an income category was used to isolate the (rare) transaction.
1. The financial institution provides a disbursement and withholds for and pays state and federal taxes.  These transactions effectively are transfers from the account and should be included.

## Investment Performance

This report is run once per year. It provides information used to determine realized and unrealized gains.

Select: All Investment, All Security

