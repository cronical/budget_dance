# invest_actl

The Python program `invest-actl-load.py` gets the master list of investment accounts from `fcast.xlsm`.  It then reads the `data/invst_*.tsv` files and computes the net flows for each account by year.

The MoneyDance Investment Performance report is named `invest-p-YYYY.tsv`. There is one for each actual year. The program reads these as well.

It ends up with 5 rows of actuals for each investment.  The values types are:

|ValType|Description|
|---|---|
|Add/Wdraw|Amount moved into or out of account|
|Rlz Int/Gn|Income + Realized Gains|
|Unrlz Gn/Ls|Unrealized gains|
|Income|Interest and Dividends|
|Gains|Realized Gains|

This can be used to look up the actuals on the balances tab. The visual basic function `gain` references the realized and unrealized gain lines for actuals. the visual basic function `add_wdraw` likewise references the first line.
