# Design of fcast.xlsm

## Purpose

This system extends the family's historical financials into the future.  It allows for planning for income/expenses as well as financial moves between accounts.   It has a tax calculator (which is far from general, but works for us). 

## Tables

The system uses a set of Excel tables.
Many of the tables represent time series where the time is based on years.  The data elements are typically financial values assoicated with a year.  For instance, the balances table tracks how balances change year by year.

The time sequence columns are labeled with 'Y' + year.  Other columns are labeled with appropriate short column labels.  The meaning of the column data depends on the state of the system.  To the left of the first forecast year, data is considered actual, while to the right it is forecast.

 An index of tables is maintained on the 'utility' worksheet, which allows the worksheet to be located by the VBA function.  This itself is a table and it is created by a Python program `index-tables.py`.

## Worksheets

Tables are distributed over a set of worksheets. Sometimes a worksheet holds more than one table.

[Worksheets](./worksheets.md)

## Excel Calculations

Use of Visual Basic (macros) allows for calculations to be done in a more readable manner.  However there is a downside.  This is that Excel cannot use its dependency trees to know what needs to occur when the macros reference or update a value with this method.  So far, I have not turned on the use of the application volitile method, as there is significant overhead, possibly causing slow performance. There is a macro, currently called calc_retir(), to perform the re-calcuations in the correct order. 

## Functions

There are Visual Basic for Applications functions in this worksheet.  There are some complex dependencies.  Currently, in some cases it is necessary to run `calc_retir` in order to complete the calculations. 

One commonly used function is `get_val`. The get_val routine requires the use of worksheet tables, and references the values by the row names and the column names.

## Conventions

- Actual account names are generally of the form *type-who-firm* where type is one of 401K, 529, BKG, BND, ESP, HSA, IRA, IRA Roth, LON, MUT.
- All table names begin with `tbl_`.
- Except where visible, such as column names and row labels, use lowercase except for acronyms.
- Use underscores between words.
- Use std abbreviations as follows:

    |	long	|	short	|
    |---|---|
    |	actual	|	actl	|
    |	annuity	|	anny	|
    |	balances	|	bals	|
    |	duration	|	dur	|
    |	investments	|	invest	|
    |	parameters	|	parms	|
    |	pension	|	pens	|
    |	retirement	|	retir	|
    |	value or valuation 	|	val	|

## Use of Python

External access to the spreadsheet is used. Mostly these are programs to transfer Moneydance actual data into the Workbook.  This is done via Python using the openxlpy library.  These files are in the `dance` subfolder.

One of these Python files, `util/index_tables.py` enumerates and indexs the tables (something oddly missing in Excel due to the fact that it is worksheet oriented). The index is stored on the utility worksheet.

The initialization of the spreadsheet is also under control of a Python utility: `setup/create_wb.py`.

