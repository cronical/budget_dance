# accounts

This worksheet lists the tracked accounts and their attributes. Some of these accounts are real accounts at financial institutions.  Others summarize sets of assets or liabilities. One account is designated as the sweep account.

The attributes are:

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| Account| The name of the account or summay set|
| Type            | A=Asset, B=Bank, C=Credit Cards, I=Investment, L=Liability, N=Loans |
| Income Txbl     | 0 if sheltered, 1 if normal taxes, 2 if deferred like treasury bond|
| Active          | 0 if inactive, 1 if active                                   |
| No Distr Plan| 0 if there is a distribution plan, 1 otherwise|
| Int Rate| The default rate for interest income when there is no history. Translates to int:reg, int:shelt or int:defered-tax based on `Income Txbl`|
| Div Rate| The default rate for dividend income when there is no history. For a bit of simplicy, this is intended to include short-term capital gains. Translates to div:reg, div:shelt based on `Income Txbl`|
| Int Tax-ex Rate| The default rate for tax exempt interest income when there is no history. (such as muni bonds)|
| Div Tax-ex Rate| The default rate for tax exempt dividend income when there is no history. (such as muni bonds in a mutual fund)|
| Cap Gains Rate | Place holder for future feature to forecast long term capital gains. Intended to represent realized gains or losses created by sales of assets and from any mutual fund LT cap gain distributions|
| Near Mkt Rate| Rate to use to override the first forecast year computed rate for unrealized gains (ie market "fluctuation")|
| Rate Cap | Rate used to cap near market computed rates|
| Fee Rate | Default rate for accounts with no history |
| Reinv Rate| Amount used to initialize the `Reinv Rate` row on the balances table. This should be called retained rate since it can be used to pay fees.|
| Notes           | Place to indicate special things about the account           |

