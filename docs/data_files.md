# Data Files

## Privacy

The data folder is excluded from github for privacy reasons.

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

```bash
tree -PD '*.tsv' --prune data/
tree -PD '*.json' --prune data/
```

### File names

Preferred format uses hyphen not underscores or spaces to separate words. Abbreviations such as IRA and HSA are forced to lowercase, to aid sorting.

## Moneydance reports and their files

(Case sensitive sort to match Moneydance)

|Report|Periods|File(s)|Used in config by|Other file use|
|:--|:--|:--|:--|:--|
|401, HSA, ESP payroll data|full years|payroll_to_savings.tsv|tbl_payroll_savings||
|529-Distr[^4]|all years|529-distr.tsv|tbl_529_distr||
|Account Balances|each year|acct-bals-*yyyy*.tsv|tbl_accounts[^1], tbl_balances[^2]|bank_actl_load.py[^3]|
|HSA - disbursements - 2|full years|hsa-disbursements.tsv|tbl_hsa_disb[^5]||
|IRA-Distr[^6]|all years|ira-distr.tsv|tbl_ira_distr|
|Income & Expense by Year|full years|iande.tsv|tbl_iande,tbl_iande_actl||
|Income & Expense YTD|Current year to date|iande_ytd.tsv|tbl_current||
|Investment IandE[^7]|full years|invest-iande.tsv|tbl_invest_iande_work||
|Investment Performance|each year|invest-p-*yyyy*.tsv|tbl_invest_actl[^7]||
|Roth-contributions2|all years|roth_contributions.tsv|tbl_roth_contributions|
|Transfers BKG detailed|full years|trans_bkg.tsv|tbl_bank_sel_invest[^10]
|Transfers to Investment Accounts by Year|full years|invest-x.tsv|tbl_invest_actl|
|Transfers-to-fcast[^9]|full years|transfers.tsv|tbl_transfers_actl||

## Other data files

### JSON input files

The following files can be prepared from an existing worksheet with the [`dance/util/extract_table.py` utility](./operations.md#extract-table), or they can be created manually. They are named according to the table that they support. 

|File|Orientation|
|:--|:--|
|aux.json|records
|ct_tax_rates.json|records|
|fed_tax_rates.json|records|
|gen_state.json|index|
|manual_actl.json|index|
|mcare_opt.json|records|
|part_b.json|records|
|pension_facts.json|index|
|people.json|index|
|social_security.json|records|
|state_tax_facts.json|index|

### Orientation

Orientation of `index` is used when the first field is a unique key.  For example `gen_state.json` might contain:

```json
{
  ...
  "ss_fed_wh": {
    "Value": 0.22,
    "Comment": "can be 7, 10, 12 or 22 see form W4-V as decimal"
  },
  "distr_fed_wh": {
    "Value": 0.2,
    "Comment": "Fed withholding used for pension & IRA distributions"
  },...
}
```

When there is no key the orientation of `records` is used. For example `fed_tax_rates.json` might start with

```json
[
  {
    "Year": 2022,
    "Range": 0,
    "Rate": 0.1,
    "Subtract": 0.0
  },
  {
    "Year": 2022,
    "Range": 20549,
    "Rate": 0.12,
    "Subtract": 410.88
  },...
```

### JSON files with testing values

The file `known_test_values.json` is set up to allow checking of the results against known historical values.

### Template tsv files

These files are used to seed their respective tables.
They are styled as a Moneydance report saved as .tsv, so the first three lines are ignored. The 4th line contains headings and subsequent lines contain data. 
Processing occurs specific to the type. In the case of taxes, indentation must be 3 spaces. The year column is for testing subtotals and is ignored during processing.

- retire_medical_template.tsv
- retire_template.tsv
- taxes_template.tsv



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
