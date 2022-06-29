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

### Inflation

You may want to consider a different series.  The default is all items in U.S. city average, all urban consumers, not seasonally adjusted.

### Required minimum distributions

At the time of writing the best source seems to be the Federal Register.  This does not need to edited unless the source changes.  

### Accounts

The data section in the `setup.yaml` needs the following sub-sections:

|Item|Description|
|:--|:--|
|path|Path from the project root where to find the saved report`.  This should be one will all the accounts you wish to use.|
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