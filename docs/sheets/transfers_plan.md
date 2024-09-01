# transfers_plan

This table simulates future transactions which move money between accounts.  

The fields are transaction year, a source (from) account and a target (to) account, an amount and a place for notes.

There is data validation on the account names to ensure they are valid and active. The complete list is generated at build time as a range out to the right. This is necessary because the drop down list function doesn't yet support dynamic arrays.

![image](../assets/images/data_validation.png)

These data are summarized and carried on the the balances tab for selected accounts in future years on the Add/Wdraw lines by the following Excel formula:

```
=SUM(
  BYROW(
    (tbl_transfers_plan[[From_Account]:[To_Account]]=tbl_balances[@AcctName])*
    HSTACK(-tbl_transfers_plan[Amount],tbl_transfers_plan[Amount]),
    LAMBDA(row,SUM(row))
    )
  *(tbl_transfers_plan[Y_Year]=INDEX([#Headers],COLUMN())))
```

The SUM phrase calculates the net change defined in the transfers_plan for this account, this year

The config.yaml file controls which accounts are handled this way. This logic should only be in the fcst_formulas section. The correct configuration has the following logic for the add/wdraw amounts:

|Accounts|Logic|
|---|---|
|Bank|Get net from IandE|
|401K,IRA,Other Assets|Get net change from Aux, since the could be both additions and subtractions|
|HSA|Get the lower of demand and available from Aux|
|All Other|Pull from transfers_plan (see note)|

Note: In the case of investment accounts there two ways to move money out.

1. Modifying the re-investment rate on the balances table to lower than 100% will cause money to move into bank account by lowering the line Y:Reinv - TOTAL, and lower the amount added into the account year end balance.

1. Adding an entry to the transfers_plan that shows a source investment account and target bank, removes the money from the source and appears as a negative under the Y:To Asst:Invest:*account* on IandE.  This has the effect of reducing the amount sent to investments for that year, making a higher amount available to send to bank.

