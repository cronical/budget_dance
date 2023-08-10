# invest_actl

This table provides annual values for 6 investment values.  It is used to look up the actuals on the balances tab. 

Provides 6 rows of actuals for each investment.  The values types are:

|ValType|Description|
|---|---|
|Add/Wdraw|Amount moved into or out of account|
|Rlz Int/Gn|Income + Realized Gains|
|Unrlz Gn/Ls|Unrealized gains|
|Income|Interest and Dividends|
|Gains|Realized Gains|
|Fees|well, fees|

## Notes

- The add/wdraw value is principal transfered, so interest payments have been removed if they are not reinvested.
- The unrealized gain value does not have the fees removed
- Requires use of lots matching.  Average cost method seems to return non sensical results for unrealized gain.
- The loading program does some error detection. If it fails, suggests some things to look at.



## Data sources

The Python program `invest-actl-load.py` uses:

1. The Moneydance performance reports. The Moneydance Investment Performance report are `data/invest-p/YYYY.tsv`. There is one for each actual year. 
1. The Moneydance balance reports, which are `data/acct-bals/YYYY.tsv`.
1. The accounts table to get the master list of investments
1. The invest_iande_work table to get the interest received from any loans

