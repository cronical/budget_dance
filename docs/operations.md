# Operations

## Export Functions

There are three commands to export data.  These write to files that are then used to reload or rebuild the workbook.

### Extract Table

Use `dance/extract_table.py` to copy the contents of an existing worksheet table the external file. The external file is defined in the data section of the configuration. Eligible tables are 

- templates
- json records
- json index

```zsh
dance/extract_table.py -h
usage: extract_table.py [-h] [--workbook WORKBOOK] [--data_only] (--table TABLE | --all | --list)

Copies table data from workbook and stores as a json or tsv output file.

options:
  -h, --help            show this help message and exit
  --workbook WORKBOOK, -w WORKBOOK
                        Source workbook. Default: data/test_wb.xlsx
  --data_only, -d       To get data not formulas
  --table TABLE, -t TABLE
                        Source table name, include tbl_
  --all, -a             Extract all eligible tables
  --list, -l            List all eligible tables
```

For example, this copies the aux table from the default workbook to a data file.

```zsh
% dance/extract_table.py -t tbl_aux
2023-06-21 14:23:19,716 - extract_table - INFO - Wrote to data/aux.json
```

Extract all:

```zsh
dance/extract_table.py -a
2023-09-08 07:21:19,911 - extract_table - INFO - Source workbook is data/test_wb.xlsx
2023-09-08 07:21:20,206 - extract_table - INFO - Wrote to data/transfers_plan.json
2023-09-08 07:21:20,504 - extract_table - INFO - Wrote to data/retire_template.tsv
...
2023-09-08 07:21:23,525 - extract_table - INFO - Wrote to data/gen_state.json
2023-09-08 07:21:23,824 - extract_table - INFO - Wrote to data/state_tax_facts.json
2023-09-08 07:21:24,137 - extract_table - INFO - Wrote to data/part_b.json
```

### Preserve

This utility preserves and restores values that are modified in eligible worksheets. The candidates are those values that are in forecast columns, or, if configured, listed non-year columns. Each value is inspected to see if it is a formula.  Only non-formulas will be exported.

The values are store in or retrieved rom external storage (typically `./data/preserve.json`).  

1. The save option copies values that are not formulas 
1. The load option compares the saved values to the values in their cells and, if different, replaces them.


```zsh
dance/preserve_changed.py -h 
usage: preserve_changed.py [-h] (-s | -l) [-w WORKBOOK] [-p PATH]

Copies changed data from tables to file or from file to various tables

options:
  -h, --help            show this help message and exit
  -s, --save            saves data from the current tab to the file
  -l, --load            loads the file data workbook
  -w WORKBOOK, --workbook WORKBOOK
                        Target workbook. Default: data/test_wb.xlsx
  -p PATH, --path PATH  The path and name of the storage file. Default=./data/preserve.json
```

```zsh
dance/preserve_changed.py -s
2023-09-08 14:51:44,958 - preserve_changed - INFO - Found 173 items from table tbl_accounts
2023-09-08 14:51:45,254 - preserve_changed - INFO - Found 27 items from table tbl_balances
2023-09-08 14:51:45,553 - preserve_changed - INFO - Found 42 items from table tbl_iande
2023-09-08 14:51:45,832 - preserve_changed - INFO - Found 128 items from table tbl_invest_iande_ratios
2023-09-08 14:51:46,126 - preserve_changed - INFO - Found 2 items from table tbl_taxes
2023-09-08 14:51:46,128 - preserve_changed - INFO - Wrote 372 items to ./data/preserve.json
```

### Current year reforecast

During the year it is handy from time to time to replace the modeled values with reprojected values. The `current` tab and the `ytd.py` program allow for this.

The command line program `ytd.py` allows the contents of the `current` (year-to-date) table to be saved into a file.  The data can be reloaded into the table after a refresh and the reprojected values can be copied into the correct cells in the `iande` table.

``` bash
usage: ytd.py [-h] [-s] [-l] [-f] [-w WORKBOOK] [-p PATH]

Copies data from ytd tab to file or from file to ytd tab and iande.

options:
  -h, --help            show this help message and exit
  -s, --save            saves data from the current tab to the file
  -l, --load            loads the file data to the current tab
  -f, --forward         carries the projected values to the first forecast year in the iande table
  -w WORKBOOK, --workbook WORKBOOK
                        Target workbook. Default=data/test_wb.xlsx
  -p PATH, --path PATH  The path and name of the storage file. Default=./data/ytd_data.json
```

So, for instance, modify the table to reproject some lines, save the file and run the save and forward functions.  The save, so it will be restored upon a re-build, and the forward to copy the values into the current year of the `iande` table.

``` zsh
dance/ytd.py -s -f
2024-04-07 12:56:37,503 - ytd - INFO - Wrote 7 items to ./data/ytd_data.json
2024-04-07 12:56:37,884 - ytd - INFO - Wrote 2 values into table tbl_iande
```

## Import functions

The `dance/util/build` shell script will completely rebuild the worksheet. Or the following utilities can rebuild portions. Use the `-h` option to see arguments.

|Utility|Purpose|
|---|---|
|`dance/iande-actl-load.py`|Copies data from input file into tab "iande" or "current"|
|`dance/invest_actl_load.py`|Copies data from input files into "invest_actl" table|
|`dance/invest_iande_load.py`|Prepares income and expense data to insert into  "tbl_invest_iande_work"|
|`dance/retire_load.py`|Prepares the retirement income or medical table from the input template|
|`dance/taxes_load.py`|Prepares the taxes table from the input template|
|`dance/transfers_actl_load.py`|Copies data from input file into "transfers_actl" table|

The following have alternate functions:

|Utility|Purpose|
|---|---|
|`dance/bank_actl_load.py`|If called from the command line, prints changes in account values due to transfers to/from bank and credit cards|


The following do not (yet) have main routines:

|Utility|Purpose|
|---|---|
|`dance/accounts_load.py`||
|`dance/balances_load.py`||
|`dance/other_actls.py`||

The following support the need to refresh data. These are usually applied annually although the year-to-date feature allows interim updates.

See also [extract](#extract-table), [preserve](#preserve), [ytd](#current-year-reforecast), and [configuration](./configuration_summary.md).

### Income and Expense

The `dance/iande_actl_load.py` module loads data into either `iande` or `current`.  

After refreshing the `current` table, it may or may not be desirable to reload the prior re-projection data using [ytd.py](#current-year-reforecast)

```bash
usage: iande_actl_load.py [-h] [-s {iande,current}] [-p PATH] [-w WORKBOOK]
                          [-f]

Copies data from input file into tab "iande" or "current".

options:
  -h, --help            show this help message and exit
  -s {iande,current}, --sheet {iande,current}
                        which sheet - iande or current
  -p PATH, --path PATH  The path and name of the input file. If not given will
                        use "data/iande.tsv" or "data/iande_ytd.tsv" depending
                        on sheet
  -w WORKBOOK, --workbook WORKBOOK
                        Target workbook
  -f, --force           Use -f to ignore warning

```

### Investments

invest_actl_load.py
invest_iande_load.py

### Other Actuals

other_actls.py

### Retirement

retire_load.py

### Taxes


#### Rebuild the taxes table

NOT CURRENTLY WRITING THE TABLE INTO THE SHEET

```zsh
dance/taxes_load.py -h      
usage: taxes_load.py [-h] [--workbook WORKBOOK] [--path PATH]

Prepares the taxes table from the input template

options:
  -h, --help            show this help message and exit
  --workbook WORKBOOK, -w WORKBOOK
                        Target workbook
  --path PATH, -p PATH  The path and name of the input file
```


### Transfers

transfers_actl_load.py


# Utility

## index_tables

The Python code, `util/index_tables.py` enumerates and indexs the tables (something oddly missing in Excel due to the fact that it is worksheet oriented). The index is stored on the utility worksheet.

