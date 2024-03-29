# Worksheets

## Index

  The worksheets are grouped together with colored tabs.  The groups are as follows:
  
|Group|Sheet|Purpose|
|---|---|---|
|acct-bal|
||[accounts](sheets/accounts.md)|lists the tracked accounts and their attributes|
||[balances](sheets/balances.md)|tracks annual changes and balance for tracked accounts|
||[transfers_plan](sheets/transfers_plan.md)|Allows for planning of transfers between accounts that do not have a distribution plan|
|income-expense|
||[iande](sheets/iande.md)|Income and expenses (and cash flow) for both actuals and forecast periods.
||[aux](sheets/aux.md)|A place for side calculations.|
||[current](sheets/current.md)|During the year, this sheet gathers the year-to-date data and allows user to forecast total year for selected lines. These then can be copied into iande.|
||[invest_iande_work](sheets/invest_iande_work.md)|Income and Expenses that relate to investments.|
|retirement|
||[retirement](sheets/retirement.md)|Retirement income streams and retirement medical expense streams|
||[retireparms](sheets/retireparms.md)|Pension, social security options, post retirement medical insurance plan selection|
|actuals|
||[other_actl](sheets/other_actl.md)|holds several tables of other actuals
||[transfers_actl](sheets/transfers_actl.md)|Gathers the transfers to and from all accounts coming from or going to banks or credit cards|
||[invest_actl](sheets/invest_actl.md)|Collects for each account categorized changes to the account value by actual time period.|
|taxes|
||[taxes](sheets/taxes.md)|computes Federal and State income taxes.|
||[capgn](sheets/cap_gain.md)|estimating taxes for the current and prior year until tax statements arrive|
||[tax_tables](sheets/tax_tables.md)|Selected federal and state tax tables.  Required mininum distribution tables.
|tables|
||[gen_tables](./sheets/gen_tables.md)|state tax information, Medicare Part B premiums, inflation, and a general state mangement|
||[utility](./sheets/utility.md)|Used by VBA functions to locate tables.

## Significant calculation flows

### Retirement Distributions

Investment accounts such as IRAs and 401Ks yield distributions based on the prior year's balance.  These values are then used to change the current year balance and income for the current year, which will then impact taxes.

![flow](./assets/images/flow_retir_distr.png)