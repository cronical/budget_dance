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

The file names do not use spaces.
Underscores are used to separate words.

## Files from Moneydance reports

The table, [below](#report-table), provides a list of Moneydance reports and the file names under which the output should be saved. 
The table also shows where the data goes and the data type code used by the configuration to indicate how to read that file.

The Periods column uses the following codes:

|Period Code|Period Meaning|
|---|---|
|All Years|Transaction Filter for all actual years|
|Annual|Summary data in annual columns (possibly just one)|
|Each Year|Separate file for each year in a folder|
|Transfers|Transfers summarized by year into annual columns|
|Transfers-X|Transfers, Detailed transaction data for all actual years|

### Report table

The report names below are prefixed with TSV_ to club them together in Moneydance.

Each year some of these need to be modified and updated to reflect the changed years.
The `All years` type should change both the start and end years assuming the desire to drop the oldest year.

In Moneydance generate each report and save the file with the default name, which will be the report name with a `.txt` extension.
The `iande_ytd` report can be skipped at year end.
Run the command `md_names yyyy` to rename and relocate these files as needed, replacing prior versions.

```zsh
[.venv] george@MacStudio:~/budget-dance
$ md_names 2025
2026-01-03 11:49:29,771 - md_names - INFO - data/invest_iande.tsv
2026-01-03 11:49:29,771 - md_names - INFO - data/529_distr.tsv
2026-01-03 11:49:29,772 - md_names - INFO - data/acct_bals/2025.tsv
2026-01-03 11:49:29,772 - md_names - INFO - data/invest_x.tsv
2026-01-03 11:49:29,773 - md_names - INFO - data/ira_distr.tsv
2026-01-03 11:49:29,773 - md_names - INFO - data/tagged.tsv
2026-01-03 11:49:29,773 - md_names - INFO - data/transfers.tsv
2026-01-03 11:49:29,774 - md_names - INFO - data/iande.tsv
2026-01-03 11:49:29,774 - md_names - INFO - data/iande_ytd.tsv
2026-01-03 11:49:29,775 - md_names - INFO - data/invest_p/2025.tsv
2026-01-03 11:49:29,775 - md_names - INFO - data/roth_contributions.tsv
2026-01-03 11:49:29,775 - md_names - INFO - data/payroll_to_savings.tsv
2026-01-03 11:49:29,775 - md_names - INFO - data/trans_bkg.tsv
```

| Report             |Periods| Final name             |Used in config by|Data type code|
|:-------------------|:--|:-----------------------|:--|:--|
| 529_distr          |All Years| 529_distr.tsv          |tbl_529_distr|md_529_distr|
| acct_bals          |Each Year| acct_bals/yyyy*.tsv    |tbl_accounts[^1], tbl_balances, bank_actl_load.py|md_acct, md_bal2|
| iande              |Annual| iande.tsv              |tbl_iande,tbl_iande_actl|md_iande_actl|
| iande_ytd          |Annual| iande_ytd.tsv          |tbl_current|md_iande_actl|
| invest_iande       |All Years| invest_iande.tsv       |tbl_invest_iande_values, tbl_invest_iande_ratios|md_invest_iande_values|
| invest_p           |Each Year| invest_p/*yyyy*.tsv    |tbl_invest_actl[^7]|md_invest_actl|
| invest_x           |Transfers| invest_x.tsv           |tbl_invest_actl|md_invest_actl|
| ira_distr          |All Years| ira_distr.tsv          |tbl_ira_distr|md_ira_distr|
| payroll_to_savings |Transfers-X| payroll_to_savings.tsv |tbl_payroll_savings|md_pr_sav|
| roth_contributions |All Years| roth_contributions.tsv |tbl_roth_contributions|md_roth|
| tagged             |All Years| tagged.tsv             |tbl_tag_sums,tbl_hsa_disb|md_tag_sums|
| trans_bkg          |Transfers-X| trans_bkg.tsv          |tbl_bank_sel_invest|md_sel_inv|
| transfers.tsv      |Transfers| transfers.tsv          |tbl_transfers_actl|md_transfers_actl|


Each of the reports should be run for the appropriate period(s) and the output saved as a .tsv file in the data folder or a subfolder, under the name given in the "Save as" column.

The Income & Expense report should not check the `Use tax date` box.  This makes it consistent with the Investment Performance report which does not have a tax date box.  If the box is checked it can lead to consistency errors when transactions span year-end.  It also seems possible to rewrite those transactions to use the prior year, instead of the following year.

Tagged sums was introduced to handle moving accounts between custodians - in particular HSA accounts, but it could probably be used to replace some other tables.

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

For example: here is production as of 11/18/2024:

```zsh
[Sep 22 18:54]  data/
├── [Nov 18 12:07]  529-distr.tsv
├── [Sep 17 15:47]  acct-bals
│   ├── [Sep 17 16:07]  2017.tsv
│   ├── [Sep 17 16:07]  2018.tsv
│   ├── [Sep 17 16:08]  2019.tsv
│   ├── [Sep 17 16:08]  2020.tsv
│   ├── [Sep 17 16:09]  2021.tsv
│   ├── [Sep 17 16:09]  2022.tsv
│   ├── [Sep 18 16:11]  2023.tsv
│   └── [Nov 18 12:15]  2024.tsv
├── [Nov  3  2022]  cap-gains.tsv
├── [Nov 18 12:12]  hsa-disbursements.tsv
├── [Nov 18 12:13]  iande.tsv
├── [Nov 18 12:14]  iande_ytd.tsv
├── [Nov 18 12:17]  invest-iande.tsv
├── [Nov 18 12:18]  invest-p
│   ├── [Dec 10  2022]  2018.tsv
│   ├── [Dec 10  2022]  2019.tsv
│   ├── [Nov 28  2022]  2020.tsv
│   ├── [May 24  2023]  2021.tsv
│   ├── [Sep  6  2023]  2022.tsv
│   ├── [Sep 18 16:08]  2023.tsv
│   └── [Nov 18 12:18]  2024.tsv
├── [Nov 18 12:20]  invest-x.tsv
├── [Nov 18 12:21]  ira-distr.tsv
├── [Nov 18 13:46]  payroll_to_savings.tsv
├── [Nov 10  2023]  retire_medical_template.tsv
├── [Aug 30 09:17]  retire_template.tsv
├── [Jan  7  2024]  roth_contributions.tsv
├── [Nov 18 13:49]  tagged.tsv
├── [Sep 18 16:21]  taxes_template.tsv
├── [Nov 18 13:50]  trans_bkg.tsv
└── [Nov 18 13:52]  transfers.tsv

3 directories, 31 files
```

## Testing files

The file `known_test_values.json` is set up to allow checking of the results against known historical values.

### Refreshing test data from production

The script `dance/util/refresh_test_data.py` copies the pertinent files from production back into the dev environment. 