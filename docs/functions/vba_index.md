# VBA Code Summary

|Function or Sub|Signature and info|
|---|---|
|ANN|Function ANN(anny_start As Date, duration As Integer, anny_rate As Double, prior_end_bal As Double, this_year As Integer, month_factor As Double) As Double|
||Return a year's value for an annuity stream based on the prior year's end balance. This version leaves all the excel dependencies visible to excel|
|get_val|Function get_val(line_key As Variant, tbl_name As String, col_name As String, Optional raise_bad_col = False) As Variant|
||Fetches a value from a given table (it must be an actual worksheet table. If the line is not found in the table, a zero is returned.. Bad columns are usually logged, but if the argument raise_bad_col is true then an error is raised.|
|IntYear|Function IntYear(yval) As Integer|
||Strips off the y on the argument (eg y2019) and returns an integer|
|log|Sub log(txt As String)|
|||
|mo_apply|Function mo_apply(start_date As Date, y_year As String, Optional end_mdy As String = "") As Double|
||Get a rational number that represents the number of months that apply in a particular year given the start date and optionally an end date. The end date is a string since there is a bug in the mac excel.. The end date represents the month of the last period to include.  the day is ignored and the last day of the month is used.|
|mo_factor|Function mo_factor(start_date As Date, duration As Double, this_year As Integer) As Double|
||Get a floating point number that represents the number of months that apply in a particular year given the start date and duration|
|ratio_to_start|Function ratio_to_start(account As String, category As String, y_year As String) As Double|
||For investment income and expense, compute the ratio to the start balance, but use the prior end balance since. That should have already been computed.  this allows the table to occur before the balances table in the compute order. To be run in a cell in the invest_iande_work table.|
|sort_tax_table|Function sort_tax_table()|
||Make sure the federal tax tables are sorted properly|
|test_get_val|Sub test_get_val()|
|||
|test_mo_apply|Sub test_mo_apply()|
|||
|test_sort|Sub test_sort()|
|||
|this_col_name|Function this_col_name() As String|
||Return the caller's column name, assuming the cell is in a table.. Otherwise generates a #value  error. Use to make formulas more portable|
|ws_for_table_name|Function ws_for_table_name(tbl_name As String) As String|
||Find out what worksheet the named table occurs on|
|y_offset|Function y_offset(y_year As String, offset As Integer) As String|
||Given a y_year offset it by the amount given, producing a new y_year|
