# accounts

This worksheet lists the tracked accounts and their attributes. Some of these accounts are real accounts at financial institutions.  Others summarize sets of assets or liabilities. One account is designated as the sweep account.

The attributes are:

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| Account| The name of the account or summay set|
| Type            | A=Asset, B=Bank, C=Credit Cards, I=Investment, L=Liability, N=Loans |
| Income Txbl     | 0 if sheltered, 1 if normal taxes|
| Active          | 0 if inactive, 1 if active                                   |
| No Distr Plan| 0 if there is a distribution plan, 1 otherwise, blank for n/a|
| Near Mkt Rate| Rate to use to override the first forecast year computed rate|
| Rate Cap | Rate used to cap computed rates|
| Reinv Rate| Amount used to initialize the `Reinv Rate` row on the balances table|
| Actl_source     | The line name where to find the actual add/wdraw amount      |
| Actl_source_tab | The table name where to find the actual add/wdraw amount     |
| Fcst_source     | The line name where to find the forecast add/wdraw amount    |
| Fcst_source_tab | The table name where to find the forecast add/wdraw amount   |
| Notes           | Place to indicate special things about the account           |

