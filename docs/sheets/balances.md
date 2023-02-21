## balances

The following fields are looked up from the account page: Type, Income Txbl, and Active.

This table has the following rows for each account.  

| ValType     | Formula                                                      |
| ----------- | ------------------------------------------------------------ |
| Mkt Gn Rate | Used to forecast *unrealized* gains.   Computed with `simple_return` for historical rows. |
| Reinv Rate | The part of realized gains that is reinvested each year. Proper modeling also requires consideration of re-investment policies, which are modeled as a re-investment rate per account per year. **TODO**: The remainder is planned to be transfered to the primary bank (new item in General State)|
| Start Bal   | Previous year's end balance                                  |
| Add/Wdraw   | The amount added to the account during the year if positive, or removed if negative. Either manual, or some rows will have formulas               |
| Rlz Int/Gn  | The actual or forecast realized gain, including income and any capital gains or losses.|
| Fees|Account and transaction fees which reduce the value of the account|
| Unrlz Gn/Ls | The unrealized gains due to market changes|
| End Bal     | Adds the start balance to each of the other change categories. |

The calculations are designed to work even if the rows are filtered or sorted.  To restore to the natural sort order sort by AcctName then ValType (using a custom sort order that needs to be defined).

### Rlz Int/Gn line 

For actuals, this value derives from the investment performance report via the [invest_actl worksheet](#invest-actl).

This report does not break out the income types.  If the accounting is done properly then the breakout for a particular investment account can be achieved via an income/expense report that selects that account. The value of the performance report 'Income' column total is equal to the value of the Investment Income report line Income - TOTAL.

For forecast periods, the [investment income and expense](#invest_iande_work) values are derived from adjusted extrapolated historical rates on line item basis. These values are then summed one way for the balances and another way for the [iande](#iande) tab.  

