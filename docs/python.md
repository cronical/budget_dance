# Use of Python

External access to the spreadsheet is provided via Python programs. Mostly these are programs to transfer Moneydance actual data into the Workbook.  This is done via Python using the `openxlpy` library.  These files are in the `dance` subfolder.

One of these Python files, `util/index_tables.py` enumerates and indexs the tables (something oddly missing in Excel due to the fact that it is worksheet oriented). The index is stored on the utility worksheet.

The initialization of the spreadsheet is also under control of a Python utility: `setup/create_wb.py`.
