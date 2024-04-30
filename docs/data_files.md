# Data Files

## Conventions

### File locations

Files are in the data folder under the project.  The data folder is excluded from github for privacy reasons.

The files that have a version each year are placed in subfolders.  The under the sub-folder the files are simply named *yyyy*.tsv.

### File types

Files are of the following types:

- Tab separated values with extension .tsv
- JSON with extension .json.  These are typically exports from tables defined in Excel. There are two types depending on the 'orientation'.  
- YAML - used for the configuration definitions

### File names

Abbreviations such as IRA and HSA are forced to lowercase, to aid sorting. 

Preferred format uses hyphen not underscores or spaces to separate words, although this remains to be cleaned up.

## Files from Moneydance reports

The table, [below](#report-table), provides a list of Moneydance reports and the file names under which the output should be saved. The table also shows where the data goes and the code by which the configuration knows to read that file.

The Periods column has the following meaning:

- All Years: Transaction Filter for all actual years
- Annual: Summary data in annual columns (possibly just one)
- Each Year: Separate file for each year in a folder
- Transfers: Transfers summarized by year into annual columns
- Transfers-X: Transfers, Detailed transaction data for all actual years

### Report table

(Case sensitive sort to match Moneydance)

|Report|Periods|Save as|Used in config by|Data type code|
|:--|:--|:--|:--|:--|
|401, HSA, ESP payroll data|Transfers-X|payroll_to_savings.tsv|tbl_payroll_savings|md_pr_sav|
|529-Distr|All Years|529-distr.tsv|tbl_529_distr|md_529_distr|
|Account Balances|Each Year|acct-bals/yyyy*.tsv|tbl_accounts[^1], tbl_balances, bank_actl_load.py|md_acct, md_bal2|
|HSA - disbursements - 2|Transfers-X|hsa-disbursements.tsv|tbl_hsa_disb|md_hsa_disb|
|IRA-Distr|All Years|ira-distr.tsv|tbl_ira_distr|md_ira_distr|
|Income & Expense by Year|Annual|iande.tsv|tbl_iande,tbl_iande_actl|md_iande_actl|
|Income & Expense YTD|Annual|iande_ytd.tsv|tbl_current|md_iande_actl|
|Investment IandE|All Years|invest-iande.tsv|tbl_invest_iande_values, tbl_invest_iande_ratios|md_invest_iande_values|
|Investment Performance|Each Year|invest-p-*yyyy*.tsv|tbl_invest_actl[^7]|md_invest_actl|
|Roth-contributions2|All Years|roth_contributions.tsv|tbl_roth_contributions|md_roth|
|Transfers BKG detailed|Transfers-X|trans_bkg.tsv|tbl_bank_sel_invest|md_sel_inv|
|Transfers to Investment Accounts by Year|Transfers|invest-x.tsv|tbl_invest_actl|md_invest_actl|
|Transfers-to-fcast|Transfers|transfers.tsv|tbl_transfers_actl|md_transfers_actl|

Each of the reports should be run for the appropriate period(s) and the output saved as a .tsv file in the data folder or a subfolder, under the name given in the "Save as" column.

## JSON input files

The files, listed below, are named according to the table that they support. 

These files can be created manually, or can be prepared from an existing worksheet with the [`dance/extract_table.py` utility](./operations.md#extract-table). 

|File|Orientation|
|:--|:--|
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

## Template tsv files

The "template" files are used to seed their respective tables.
They are styled as a Moneydance report saved as .tsv, so the first three lines are ignored. The 4th line contains headings and subsequent lines contain data. 
Processing occurs specific to the type. In the case of taxes, indentation must be 3 spaces. 

- retire_medical_template.tsv
- retire_template.tsv
- taxes_template.tsv

The above files can be prepared manually or extracted from an existing worksheet with the [`dance/extract_table.py` utility](./operations.md#extract-table).

## Listing data files

A listing of the files can be had with 

```bash
tree -PD '*.tsv' --prune data/
tree -PD '*.json' --prune data/
```

## Testing files

The file `known_test_values.json` is set up to allow checking of the results against known historical values.
