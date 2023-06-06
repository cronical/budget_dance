# Operations

The following support the need to refresh data. These are usually applied annually although the year-to-date feature allows interim updates.

## Actuals

### Bank 
bank_actl_load.py

### Income and Expense

The `dance/iande_actl_load.py` module loads data into either `iande_actl` or `current`.  For actual income and expense lines `iande` references the `iande_actl` table so that its easier to update.  

After refreshing the `current` table, it may or may not be desirable to reload the prior re-projection data using [ytd.py](#year-to-date).

```bash
usage: iande_actl_load.py [-h] [-s {iande_actl,current}] [-p PATH] [-w WORKBOOK] [-f]

Copies data from input file into tab "iande_actl" or "current" after doing some checks.

options:
  -h, --help            show this help message and exit
  -s {iande_actl,current}, --sheet {iande_actl,current}
                        which sheet - iande_actl or current
  -p PATH, --path PATH  The path and name of the input file. If not given will use "data/iande.tsv" or "data/iande_ytd.tsv"
                        depending on sheet
  -w WORKBOOK, --workbook WORKBOOK
                        Target workbook
  -f, --force           Use -f to ignore warning
```

#### Year-to-date and reprojection

During the year it is handy from time to time to replace the modeled values with reprojected values. The current tab and the `ytd.py` program allow for this.

The command line program `ytd.py` allows the contents of the ytd table to be saved into a file.  The data can be reloaded into the table after a refresh and the reprojected values can be copied into the correct cells in the iande table.

``` bash
usage: ytd.py [-h] [-s] [-l] [-f] [-w WORKBOOK] [-p PATH]

Copies data from ytd tab to file or from file to ytd tab and iande.

options:
  -h, --help            show this help message and exit
  -s, --save            saves data from the current tab to the file
  -l, --load            loads the file data to the current tab
  -f, --forward         carries the projected values to the first forecast year in the iande table
  -w WORKBOOK, --workbook WORKBOOK
                        Target workbook. Default=data/test_wb.xlsm
  -p PATH, --path PATH  The path and name of the storage file. Default=./data/ytd_data.json
```


### Investments

invest_actl_load.py
invest_iande_load.py

### Other Actuals

other_actls.py

### Retirement

retire_load.py

### Taxes

#### New year - new tax rates

Pull the IRS data as a .csv file. Use `bracket_fix.py` to transform into the correct format.

For example:

```zsh
dance/bracket_fix.py data/2022_tax_brackets_irs.csv 
0,0.10,0
20549.0,0.12,410.8800000000001
83550.0,0.22,8766.0
178150.0,0.24,12329.0
340100.0,0.32,39537.0
431900.0,0.35,52494.0
647850.0,0.37,65451.0
Copy the above numbers into the table and add the year
```

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

# Setup

See [Setup](./setup.md).

# Utility

## index_tables

The Python code, `util/index_tables.py` enumerates and indexs the tables (something oddly missing in Excel due to the fact that it is worksheet oriented). The index is stored on the utility worksheet.

### Extract Table

Use `dance/util/extract_table.py` to copy the contents of an existing table to a `json` formatted file.

```zsh
usage: extract_table.py [-h] [--workbook WORKBOOK] [--table TABLE] [--orient {index,records}] [--json JSON] [--data_only]

Copies table from workbook and stores as a json output file

options:
  -h, --help            show this help message and exit
  --workbook WORKBOOK, -w WORKBOOK
                        Source workbook
  --table TABLE, -t TABLE
                        Source table name
  --orient {index,records}, -o {index,records}
                        Use records if 1st fld not unique
  --json JSON, -j JSON  Name of the json file to store the output.
  --data_only, -d       To get data not formulas
```


For example, this copies the aux table from a worksheet called test_wb.xlsm to a data file.

```zsh
dance/util/extract_table.py -w data/test_wb.xlsm -t tbl_aux -j data/aux.json -o records
```