# balances

This table uses the "folding" techique in order to calculate the ending balance. To support this the three leading fields are:

1. Key - normally hidden, this field is the Account followed by a colon and then the ValType.
1. ValType
1. Account

The after this follow fields looked up from the account page: Type, Income Txbl, and Active, No Distr Plan.

This table has the following rows for each account, as shown for the account '*account*':

|Key|Description|
| ------------------ | ------------------------------------------------------------ |
|*account*|A blank row|
|*account*:Start Bal| Previous year's end balance, except the first one, which is pulled in from actuals at build time|
|*account*:Add/Wdraw|The amount added to the account during the year if positive, or removed if negative. Formula set at build-time based on config. For example in forecast periods bank accounts sweep any residual from income and expense with `=XLOOKUP("TOTAL INCOME - EXPENSES",tbl_iande[Key],tbl_iande[Y2023])`|
|*account*:Retain|A blank row marking the retained realized interest/gain|
|*account*:Retain:Rlz Int/Gn|For banks, interest pulled from the aux table; for investments, realized gains and income, pulled from invest_iande_work. |
|*account*:Retain:Reinv Rate|The reinvestment rate pulled from the accounts table.|
|*account*:Retain - PRODUCT|The amount retained calculated at the "fold" line with the product aggregation|
|*account*:Unrlzd|A blank row marking unrealized gain or loss section|
|*account*:Unrlzd:Actl Unrlz|Actual unrealized gain or loss - only used for actual periods, where its pulled from invest_actl with `=XLOOKUP("Unrlz Gn/Ls"&[@AcctName],tbl_invest_actl[Key],tbl_invest_actl[Y2022])`|
|*account*:Unrlzd:Fcst|A blank row marking forecast unrealized gain or loss section|
|*account*:Unrlzd:Fcst:I Start Bal|For investments only (banks don't have unrealized gains), the prior period ending balance: `=XLOOKUP([@AcctName]& " - TOTAL",[Key],[Y2022])`|
|*account*:Unrlzd:Fcst:Mkt Gn Rate|The forecast market gain rate - usually: `=XLOOKUP([@AcctName]&":Unrlz Gn/Ls:rate",tbl_invest_iande_work[Key],tbl_invest_iande_work[Y2024])`.  But first forecast period comes from the accounts table: `=XLOOKUP([@AcctName],tbl_accounts[Account],tbl_accounts[Near Mkt Rate],0)*[@Active]`|
|*account*:Unrlzd:Fcst - PRODUCT|The amount of market gain forecast, calculated at the "fold" line with the product aggregation|
|*account*:Unrlzd - TOTAL|The actual or forecast unrealized bgain calculated at the "fold" line with the SUM aggregation|
|*account*:Fees|Forecast fees for investment accounts: `=XLOOKUP([@AcctName]& ":Investing:Account Fees:value",tbl_invest_iande_work[Key],tbl_invest_iande_work[Y2023],0)`|
|*account* - TOTAL|The actual or forecast ending balance. Sum of above|

The calculations are designed to work even if the rows are filtered.  But sorting may produce strange results. 

## Rlz Int/Gn line 

For actuals, this value derives from the investment performance report via the [invest_actl worksheet](#invest-actl).

This report does not break out the income types.  If the accounting is done properly then the breakout for a particular investment account can be achieved via an income/expense report that selects that account. The value of the performance report 'Income' column total is equal to the value of the Investment Income report line Income - TOTAL.

For forecast periods, the [investment income and expense](#invest_iande_work) values are derived from adjusted extrapolated historical rates on line item basis. These values are then summed one way for the balances and another way for the [iande](#iande) tab.  

