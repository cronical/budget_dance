# aux
This is a set of rows needed to establish forecasts in some cases.  

The rows may be input or calculated.  The need arises for aux data and calcs, for instance, in handling 401K accounts, where the EE contribution is tax deductable but is only part of the amount for add/wdraw at the balance level.  That value plus the pre-tax deductions amounts from the paychecks need to be summed to produce the W2 exclusions.  This is the place where those calcs happen. 

The table uses the "folding" method to allow aggregations, such as PRODUCT, MIN and TOTAL. Aggregated items are typically called for in another table. 

Social security withholding is a good example. Setting up the nesting as follows, allows the calculation to be done naturally without creating unwanted dependencies:

|Key|Formula|
|---|---|
|WH:Soc Sec||
|WH:Soc Sec:G||
|WH:Soc Sec:G:Base||
|WH:Soc Sec:G:Base:Cap|=XLOOKUP("Social Security Wage Cap",tbl_manual_actl[Item],CHOOSECOLS(tbl_manual_actl[#Data],-1))|
|WH:Soc Sec:G:Base:Gross|=XLOOKUP(CHOOSECOLS(TEXTSPLIT([@Key],":"),3)&" - Earned income - TOTAL",TRIM(tbl_iande[Account]),tbl_iande[Y2023])|
|WH:Soc Sec:G:Base - MIN|=MIN(H58:H59)|
|WH:Soc Sec:G:Rate|=XLOOKUP("Social Security FICA rate",tbl_manual_actl[Item],CHOOSECOLS(tbl_manual_actl[#Data],-1))|
|WH:Soc Sec:G - PRODUCT|=PRODUCT(H60:H61)|

The year column references, such as Y2023, are provided for each column at build time as are the aggregation formulas.

### Definitions

The rows are defined in `config.yaml` using the `data:hier_insert_paths:` and `data:hier_alt_agg:` keys.
