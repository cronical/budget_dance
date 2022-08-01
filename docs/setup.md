# Setting up the spreadsheet

## Summary of steps

1. Save certain reports from Moneydance to the `data` folder.
1. Acquire a registration key for the bureau of labor statistics (for inflation data)
1. Edit the control file: `dance/setup/setup.yaml`
1. Run `dance/setup/create_wb.py`

## Reports

1. The most current Account Balances should be saved as a tab-separated values file. This is used to create the Accounts worksheet.  Its name will be referenced in the `setup.yaml`.  The balances are not used, except that when they are zero, the account will be ignored unless it is specifically mentiond in the `include_zeros` section of the YAML.
1. Another instance of the Account Balances is used to establish the opening balances on the Balances sheet. This may or may not be the same as the other Account Balances file.  If an earlier file is used, history can be included in the Balances sheet.

## API key

The system copies the inflation data to faciliatate planning.  To do this an API key is needed.  This is free they only want an email address.  Register here: <https://data.bls.gov/registrationEngine/>.  The API key should be stored in ./private/api_keys.yml. The rows of this file are expected to be simply a site code and the key value, such as below:

```yaml
bls: 7b50d7a727104578b1ac86bc27caff3f
```

## The setup control file

The control file is `dance/setup/setup.yaml`.

### Global Settings

The following values are global in nature:

|Item|Purpose|Example|
|:--|:---|---|
|start_year |Integer of 1st year to use for time series| 2018
|end_year |Last Year of the time series| 2030
|year_column_width|Column size for years| 12
|first_forecast_year |First year that is considered a forecast. Prior years are considered actual| 2022
|zoom_scale|Scaling factor for all sheets| 135 # how to scale the worksheets
|bank_interest|Moneydance category used to convey bank interest to the account balances| Income:I:Invest income:Int:Bank

### Sheet groups

Sheets are grouped together in sheet groups using the `sheet_group` definitions.  Each sheet is assigned to a group and thus shares the color and table style.

### Sheets

This section defines the layout and sometimes the data to be loaded into the sheet. It is a list of definition of each sheet.  So at that level it looks like:

```yaml
sheets:
  accounts:
  balances:
  iande:
  ...
```

### Table Definitions

Within each sheet are the list of tables. Most sheets only have one.  Here's an example with two:

```yaml
retireparms:
  sheet_group: retirement
  tables:
  - name: tbl_retire_parms
  - name: tbl_pens_facts
```
By convention all the table names start with `tbl_`.

The table definition consists of various fields, some of which are optional and/or defaulted.

|Item|Purpose|Required?|Default|
|:--|:---|---|---|
|title|The title that is place above the table in Excel|Y||
|include_years|True if there is a time series for the years|N|False|
|columns|A list of the column definitions (name and width) that are included before the time seriex|Y||
|hidden|A list of columns to hide|N|Show every column
|data|definitions where to get the data for the initial load|N|Don't load data|
|title_row|When there is more than one table, locate this table on the sheet|N|2
|start_col|The first column of the table on the sheet (A=1,B=2...)|N|1|

### Data definitions

The data definitions are purpose built to support the target table, but there are some elements that are common.  Some data definitions are closely related, so, to prevent duplication, the yaml reference/override notation is used (& and *).  

|Item|Purpose|Used for|
|:--|:---|---|
|source|local to reference local files; remote to pull data over internet. remote to pull data over internet. internal is used to create the table/sheet cross reference.|
|type|These codes are used by the program select the processing logic to use. md_acct - for accounts, md_bal for balances, md_iande_actl for income and expense sheets|local|s
|path|path relative to project folder|for local sources|
|group|Specific Moneydance groupings to include|Accounts, Balances|
|no_details_for|For these groupings create rows only at the grouping level, no details. Investments here means to summarize to the investment level and don't carry over the securities.|Accounts|
|include_zeros|Accounts listed here will be carried over even if the balance is zero|Accounts|
|tax_free_keys|Mark the accounts that are not subject to current income tax|Accounts|
|site_code|BLS, or FEDREG. Used to determine which site to reference|remote|
|api_key|If needed. A reference to the api_key which is stored in ./private/api_keys.yml|remote|
|table|Defines how to locate a table in HTML|remote|
|table.find_method|caption - only supported method|remote|
|table.method_parameters|parameters for the method, specifically the text to search for in the caption.|remote|

### Specific Sheets & Tables

#### Inflation

You may want to consider a different series.  The default is all items in U.S. city average, all urban consumers, not seasonally adjusted.

#### Required minimum distributions

At the time of writing the best source seems to be the Federal Register.  This does not need to edited unless the source changes.  

#### Accounts

The data section in the `setup.yaml` needs the following sub-sections:

|Item|Description|
|:--|:--|
|path|Path from the project root where to find the saved report`.  This should be one with all the accounts you wish to use.|
|group|this is a list of the summary levels you wish to use in your plan.  The items can either be the categories that Moneydance uses such as Bank Accounts, or it can be summary accounts that you have created (accounts that have sub-accounts)|
|no_details_for|If you have summary accounts that cover all the items in a category, then you can use those instead of the leaf accounts. By listing the category hear the detail accounts will be ignored.
|include_zeros|Usually zero balance accounts will be ignored.  If the account is entered here, it will be carried forward.  This can be useful if its a brand new account with no balance or if its an old account that had a balance in the historical period.
|tax_free_keys|A list of keywords that will be used to determine how the tax status of the account will be initialized.|

Example:

```yaml
path: ./data/2022 Account Balances.tsv
group:
- Bank Accounts
- Credit Cards
- Real Estate
- Other Asset
- Liabilities
- Mortgage Loans
- Non Mort Loans
no_details_for:
- Assets
- Loans
include_zeros:
- My old HSA
- My old 401K
tax_free_keys:
- 401K
- "529"
- IRA
```