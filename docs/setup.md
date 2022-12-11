# Setting up the spreadsheet

## Summary of steps

1. Save certain reports from Moneydance to the `data` folder.
1. Acquire a registration key for the bureau of labor statistics (for inflation data)
1. Edit the control file: `dance/setup/setup.yaml`
1. Run `dance/setup/create_wb.py`

## Conventions

### File types

Set up files are either 

- tab separated values with extension .tsv
- JSON with extension .json.  These are typically exports from tables defined in Excel. There are two types depending on the 'orientation'.  
- YAML - used for the setup config definitions

### File locations

Files are in the data folder under the project.  The data folder is not included in the git repository. 

To make more manageable, the files that have a version each year are placed in subfolders.  The under the sub-folder the files are simply named *yyyy*.tsv.

A listing of the files can be had with 

`tree -PD '*.tsv' --prune data/`

### File names

Preferred format uses hyphen not underscores or spaces to separate words. Abbreviations such as IRA and HSA are forced to lowercase, to aid sorting.

## Reports and their files

|Report|Periods|File(s)|Used in config by|Other file use|
|:--|:--|:--|:--|:--|
|Account Balances|each year|acct-bals-*yyyy*.tsv|tbl_accounts[^1], tbl_balances[^2]|bank_actl_load.py[^3]|
|529-Distr[^4]|all years|529-distr.tsv|tbl_529_distr||
|401, HSA, ESP payroll data|full years|payroll_to_savings.tsv|tbl_payroll_savings||
|HSA - disbursements|full years|hsa-disbursements.tsv|tbl_hsa_disb[^5]||
|Income & Expense by Year|full years|iande.tsv|tbl_iande,tbl_iande_actl||
|Investment IandE[^7]|full years|invest-iande.tsv|tbl_invest_iande_work||
|Investment Performance|each year|invest-p-*yyyy*.tsv|tbl_invest_actl[^7]||
|IRA-Distr[^6]|all years|ira-distr.tsv|tbl_ira_distr|
|Transfers-to-fcast[^9]|full years|transfers.tsv|tbl_transfers_actl||
|Transfers to Investment Accounts by Year|full years|invest-x.tsv|tbl_invest_actl|
|Transfers BKG detailed|full years|data/trans_bkg.tsv|tbl_bank_sel_invest[^10]







## API key

The system copies the inflation data to faciliatate planning.  To do this an API key is needed.  This is free they only want an email address.  Register here: <https://data.bls.gov/registrationEngine/>.  The API key should be stored in ./private/api_keys.yml. The rows of this file are expected to be simply a site code and the key value, such as below:

```yaml
bls: 7b50d7a727104578b1ac86bc27caff3f
```

## The setup control file

The control file is `dance/data/setup.yaml`.

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

|Item|Purpose|Default|
|:--|:---|---|
|**title**|The title that is place above the table in Excel||
|**columns**|A list of the column definitions (name and width) that are included before the time |
|title_row|When there is more than one table, locate this table on the sheet|2
|start_col|The first column of the table on the sheet (A=1,B=2...)|1|
|include_years|True if there is a time series for the years|False|
|hidden|A list of columns to hide|Show every column
|data|definitions where to get the data for the initial load|Don't load data|
|[actl_formulas](#actual-and-forecast-formulas) |Specify formulas for actuals.|
|[fcst_formulas](#actual-and-forecast-formulas)|Specify formulas for forecast periods.|
|highlights|Specify Excel conditional formatting|
|[dyno_fields](#build-time-created-fields)|a way to determine values at build time|

#### Data definitions

The data definitions are purpose built to support the target table, but there are some elements that are common.  Some data definitions are closely related, so, to prevent duplication, the yaml reference/override notation is used (& and *).  

|Item|Purpose|Use context|
|:--|:---|---|
|source|local to reference local files; remote to pull data over internet. remote to pull data over internet. internal is used to create the table/sheet cross reference.|
|type|These codes are used by the program select the processing logic to use. [See supported types](#supported-types)|local|
|path|path relative to project folder|for local sources, the path and name of the primary input file|
|file_set|for items that require additional files, the set of files is further defined|
|- base_path| A folder name with the trailing slash|
|- prefix| Further select files with a prefix|
|group|Specific Moneydance groupings to include. Moneydance uses these to categorize accounts.  Its things like: Assets, Bank Accounts, Credit Cards...  |Accounts, Balances|
|no_details_for|For these groupings create rows only at the grouping level, no details. Investments here means to summarize to the investment level and don't carry over the securities.|Accounts|
|include_zeros|Accounts listed here will be carried over even if the balance is zero|Accounts|
|tax_free_keys|Mark the accounts that are not subject to current income tax|Accounts|
|site_code|BLS, or FEDREG. Used to determine which site to reference|remote|
|api_key|If needed. A reference to the api_key which is stored in ./private/api_keys.yml|remote|
|table|Defines how to locate a table in HTML|remote|
|table.find_method|caption - only supported method|remote|
|table.method_parameters|parameters for the method, specifically the text to search for in the caption.|remote|
|[hier_insert_paths](#inserting-rows-for-future-use) |Some line items are do not yet exist or are not yet populated in Moneydance. This is a way to insert them within the hierarchy so they can be used for forecasting.|iande|

##### Supported Types

|Type|Purpose|
|:--|:---|
|md_acct|Processes the account extract from Moneydance|
|md_bal|Processes the balances extract from Moneydance|
|md_iande_actl|Processes the income and expense extract from Moneydance to create the iande and iande_actl sheets|
|md_transfers_actl|Sets up the non-investment actual transfers|
|md_invest_actl|Sets up the investment actual transfers|
json_index|Imports entire table previously exported via `dance/util/extract_table.py` using the `-o index` option. Suitable when the table has a unique key.
json_records|Imports entire table previously exported via `dance/util/extract_table.py` using the `-o index` option. Suitable when the table does not have a unique key.

##### Inserting Rows for Future Use

The income and expense report in MoneyDance filters out categories that have no transactions.  This leads to a need to insert those rows in the `tbl_iande` and `tbl_iande_actl` tables. For example, future social security payouts should subtotal into retirement income. 

An optional key is used to define these rows. The specification needs to contain the full hiearchy information so that it can be inserted into the right place.  

```yaml
data: ...
  hier_insert_paths:
    - Income: "Income:I:Retirement income:Social Security:SS-G"
    - Income: "Income:I:Retirement income:Social Security:SS-V"
```
Include only those lines that are not headings or totals; those will be constructed and inserted as well as the specified data lines.

#### Actual and Forecast Formulas

There are two optional keys to allow formulas to be established for the years section: `actl_formulas` and `fcst_formulas`.  They work the same way but apply to different columns. 

Each section consists of a list of rules.  The rules have the following parts:
|Key word|Description|
|---|---|
|base_field|The name of the column that is used for matching|
|matches|A list of values by which to match rows. This could match a single row or many rows.|
|formula|The formula to use for the selected year columns (actual or forecast)
|first_item|Optional. In some cases the first item or items of the series needs to be different. If supplied it may be a keyword `skip`. If it starts with `=` then it is a formula that will be used in the first place. Otherwise, it will be a constant or a list of constants separated by `,`. In that case it will be applied to the first *n* positions.|

For example, if there is a key `fcst_formulas` under the table, it is used to set formulas for the forecast columns.  Each column receives the same formula, but they can vary by row.  The structure is setup like this:

```yaml
fcst_formulas:
  - base_field: ValType
    matches:
    - Rate
    formula: =.03
  - base_field: ValType
    matches:
    - Add/Wdraw
    formula: =add_wdraw( [@AcctName],this_col_name())
  - base_field: ...
```

#### Build-time created fields

Some tables need a way to determine values at build time. The `dyno_fields` section may be directly under the table.

```yaml
dyno_fields:
  - base_field: Account
    matches:
      - 401K - GBD - TRV
      - CHET - Fidelity
    actions:
      - target_field: Fcst_source
        suffix: "- wdraw"
      - target_field: Fcst_source_tab
        constant: tbl_aux
  - base_field: ...
```
the `matches` list is a list of values to be matched agains the field. There is a special case if just a single *, meaning all.

The target field should be previously defined, but it is filled in by this logic.  The commands available are:
- suffix - something added to the matched item
- constant - a value that is always the same
- formula - an Excel formula

##### Formula Specifics

- Always start the formula with a leading equals sign.
- Constants are fine, but remember to use the leading equals sign
- Structured table references are supported and recommended.  
- Refer to this column with the VBA function `this_col_name()`
- Many VBA functions are designed to be used in formulas

#### Highlights

For example the following puts a line between the actual and forecast periods. The anchor, (ampersand) allows other tables to use the same by using `*past_future`

```yaml
  highlights: 
    present: &past_future
      formula: =A$2=get_val("first_forecast","tbl_gen_state","Value") # ref is to heading row
      border:
        edges: 
        - left
        style: thin
        color: B50000
```

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



[^1]: The most recent is best so as to contain all current accounts. This is used to create the Accounts worksheet.  The balances are not used, except that when they are zero, the account will be ignored unless it is specifically mentiond in the `include_zeros` section of the YAML.

[^2]:  Another instance of the Account Balances is used to establish the opening balances on the Balances sheet. This may be for a different year.  If an earlier file is used, history can be included in the Balances sheet.

[^3]: All history years must be available in order to compute the flows to/from bank accounts and credit cards.

[^4]: 529 Distributions depend on the tag `529-Distr` being used to make distributions but not inheritance or transfers.  Thus on the iande table it defrays the college expenses.

[^5]: These data are used to compute medical payments made from HSA accounts by year.

[^6]: This is a transaction filter report using the tag `IRA-Txbl-Distr`

[^7]: This is a transaction filter that selects income and expense categories that are required to only apply to investments.

[^8]: Investment actuals requires the transfers file and the performance files. It also depends on the data from the investment expenses to already be in place.

[^9]: This requires that if the Passthru account is used, it must only be used to transfer funds to/from banks.  In other words there is an assumption that it does not mask any movement to/from income or expense items.  Those must be directly in the investment account.

[^10]: Source accounts: All bank, credit card, income, expense and all HSA accounts. Target Accounts: All asset, liability & loan. The HSA accounts (a subset of investments) are needed since they sometimes transfer to the medical providers.


