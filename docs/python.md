# Use of Python

External access to the spreadsheet is provided via Python programs. Mostly these are programs to transfer Moneydance actual data into the Workbook.  This is done via Python using the `openxlpy` library.  These files are in the `dance` subfolder.

## Operations

The following support the need to refresh data. These are usually applied annually although the year-to-date feature allows interim updates.

### Actuals

#### Bank 
bank_actl_load.py

#### Income and Expense

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

##### Year-to-date and reprojection

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


#### Investments

invest_actl_load.py
invest_iande_load.py

#### Other Actuals

other_actls.py

#### Retirement

retire_load.py

#### Taxes

bracket_fix.py
taxes_load.py

#### Transfers

transfers_actl_load.py

## Setup

## Create workbook

The initialization of the spreadsheet is also under control of a Python utility: `setup/create_wb.py`.

## Utility

### index_tables

The Python code, `util/index_tables.py` enumerates and indexs the tables (something oddly missing in Excel due to the fact that it is worksheet oriented). The index is stored on the utility worksheet.



