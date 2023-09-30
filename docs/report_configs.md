# Moneydance report definitions

This page describes the reports which are used to generate the actual data.

## 401, HSA, ESP payroll data

A "Transfers, Detailed" report selecting checking accounts, all passthru accounts.  Due to odd circumstances such as return of excess 401K contributions, and employer HSA contributions, some income & expense accounts may be added.

## 529-Distr

529 Distributions depend on the tag `529-Distr` being used to make distributions but not inheritance or transfers.  Thus on the iande table it defrays the college expenses.

## Account Balances

The most recent is best so as to contain all current accounts. This is used to create the Accounts worksheet.  The balances are not used, except that when they are zero, the account will be ignored unless it is specifically mentiond in the `include_zeros` section of the YAML.

Another instance of the Account Balances is used to establish the opening balances on the Balances sheet. This may be for a different year.  If an earlier file is used, history can be included in the Balances sheet.

All history years must be available in order to compute the flows to/from bank accounts and credit cards.

## HSA - disbursements - 2

These data are used to compute medical payments made from HSA accounts by year.

## IRA-Distr

This is a transaction filter report using the tag `IRA-Txbl-Distr`.

## Income & Expense by Year

Using "Income and Expenses" report, for all actual years, grouped by year, showing all expenses and all income.

## Income & Expense YTD

Using "Income and Expenses" report, for the Year to date period, not grouped, showing all expenses and all income.

## Investment IandE

This is a transaction filter that selects income and expense categories that are required to only apply to investments.

### Certain categories

Two situations have arisen when the use of categories made sense.

1. An inheritance which was transfered directly to an investment account.  In this case an income category was used to isolate the (rare) transaction.
1. The financial institution provides a disbursement and withholds for and pays state and federal taxes.  These transactions effectively are transfers from the account and should be included.

## Investment Performance

This report is run once per year. It provides information used to determine realized and unrealized gains.

Select: All Investment, All Security

Investment actuals requires the transfers file and the performance files. It also depends on the data from the investment expenses to already be in place.

## Roth-contributions2

This is a "Transaction Filter" report, selecting all dates for transactions with tag "roth", showing splits and full account paths with subtotals by category.

## Transfers BKG detailed

Source accounts: All bank, credit card, income, expense and all HSA accounts. Target Accounts: All asset, liability & loan. The HSA accounts (a subset of investments) are needed since they sometimes transfer to the medical providers.

## Tranfers to Investment Accounts by Year

This report can be run once for all actual year periods.  It provides transfers in/out of the investment accounts.

Source accounts: 

- All Bank except[^1]
- All Credit Card
- Certain categories[^2]

Target accounts: All Investment

[^1]: Except any accounts that acts as a passthru account to handle separate dividend and dividend reinvested transactions - see [Passthru](./accounting.md#passthru)). Such accounts have to be excluded from true transfers. 
[^2]: Normally funds to/from investments go through bank accounts (or passthru accounts).  But if that is not the case, direct movement to income or expense categories should be accounted for here.  For instance if an RMD is paid out of an IRA and the brokerage withhold income taxes, the income tax category could be listed here.

## Transfers-to-fcast

Source accounts: All bank, All Income, All Credit Card, All Expense
Target accounts: All Load, All Asset, All Liability

Security and Investments are handled via the performance report

This requires that if the Passthru account is used, it must only be used to transfer funds to/from banks.  In other words there is an assumption that it does not mask any movement to/from income or expense items.  Those must be directly in the investment account.







