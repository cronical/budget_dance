## retirement

Plans out income streams and post-retirement medical expenses.  This affects both the balances and the iande tabs.

Retirement medical are modeled here.   Deductibles and copays are in 'other'. These values are posted as totals in the premium lines of IANDE and are meant to represent all net medical expenses.

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
|Item|A computed key, composed of type, whose, and firm.|
|Who|Initials of who owns this account or JNT for joint. Normally hidden.|
|Type|See [conventions](../fcast.md#conventions). Normally hidden.|
|Firm|The firm holding the account. Normally hidden.|
|Election|A code for the distribution election on this item.|
|Start Date|Expected start date for the distribution or expense|
|Anny Dur Yrs|If an annuity is elected, how many years should it run.|
|Anny Rate|The rate used for the annuity|
|Yearly|For non-annuity ongoing values (pensions), yearly amount.|

