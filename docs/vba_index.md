# VBA Code Summary

|Function or Sub|Signature and info|
|---|---|
|age_as_of_date|Function age_as_of_date(inits As String, dt As Date) As Double|
||Return the age attained by an account owner in a given year. Deprecation candidate - appears not to be used|
|age_of|Function age_of(inits As String, y_year As String) As Integer|
||Return the age attained by an account owner in a given year|
|agg|Function agg(y_year As String, by_tag As Variant, Optional agg_method = "sum", Optional tag_col_name As String = "Tag") As Double|
||Aggregate (default is sum) up the values in the table containing the calling cell for a year where the by_tag is found in the tag column.. Use of this can help avoid the hard coding of addresses into formulas. By default the tag column is "tag" but an alternate can be provided. Other agg_methods are "min" and "max"|
|agg_table|Function agg_table(tbl_name As String, y_year As String, by_tag As String, Optional agg_method = "sum", Optional tag_col_name As String = "Tag") As Double|
||Aggregate (default is sum) up the values in the named table for a year where the by_tag is found in the tag column.. Use of this can help avoid the hard coding of addresses into formulas. By default the tag column is "tag" but an alternate can be provided. Other agg_methods are "min" and "max". A second and third criteria may be provided by extending the by_tag and the tag_col_name as follows:. A delimiter is included in the strings to allow two values to be provided.the delimiter is stile (|). The there should be exactly 0 or 1 or 2 delimiters, andthe by_tag and tag_column_name should agree|
|ANN|Function ANN(anny_start As Date, duration As Integer, anny_rate As Double, prior_end_bal As Double, this_year As Integer, month_factor As Double) As Double|
||Return a year's value for an annuity stream based on the prior year's end balance. This version leaves all the excel dependencies visible to excel|
|annuity|Function annuity(account As String, y_year As String) As Double|
||Return a year's value for an annuity stream based on the prior year's end balance. Fetches the start date, duration and annual annuity rate from tbl_retir_vals. Rounds to whole number|
|bal_agg|Function bal_agg(y_year As String, val_type As String, Optional acct_type As String = "*", Optional txbl As Integer = 1, Optional active As Integer = 1) As Double|
||Get the sum of values from the balances table for a year and type, optionally further qualified by acct type,taxable status,active status. Wild cards are ok as are excel functions like "<>" prepended to the values for strings. Note all the criteria fields must have values - suggest using na if there is no value such as for an election.|
|CT_Tax|Function CT_Tax(tax_Year As Integer, taxable_Income As Double) As Double|
||Calculate the ct income tax for a given year and taxable income amount. The so called initial tax calculation only.. Table is not setup exactly like federal - it uses the traditional method not the subraction method.. Gets a result of zero if year not in the table.|
|CT_Tax_Range|Function CT_Tax_Range(ParamArray parms() As Variant) As Double|
||Pass in either. A single range of two values to get ct initial tax; or. A list of ranges of single values - count of 2. Encapsulates ct_tax. First value is tax table year as integer. Second value is ct taxable income|
|Fed_Tax_CapGn|Function Fed_Tax_CapGn(tax_Year As Integer, taxable_Income As Double, totCapGn As Double) As Double|
||Computes the resulting federal tax with capital gains portion at 15%. The input should include qualified dividends|
|Fed_Tax_Range|Function Fed_Tax_Range(ParamArray parms() As Variant) As Double|
||Pass in either. A single range of two or three values to get federal tax; or. A list of ranges of single values - either 2 or 3. Encapsulates fed_tax_capgn. First value is tax table year as integer. Second value is taxable income. Third is the capital gains. If the 3rd value is zero then returns the federal tax without adjusting for capital gains|
|Federal_Tax|Function Federal_Tax(tax_Year As Integer, taxable_Income As Double) As Double|
||Calculate the federal income tax for a given year and taxable income amount. Gets a result of zero if year not in the table.|
|get_val|Function get_val(line_key As Variant, tbl_name As String, col_name As String, Optional raise_bad_col = False) As Variant|
||Fetches a value from a given table (it must be an actual worksheet table. If the line is not found in the table, a zero is returned.. Bad columns are usually logged, but if the argument raise_bad_col is true then an error is raised.|
|IntYear|Function IntYear(yval) As Integer|
||Strips off the y on the argument (eg y2019) and returns an integer|
|is_forecast|Function is_forecast(y_year As String) As Boolean|
||Determine if this year is a forecast year|
|last_two_parts|Function last_two_parts(cat As String, Optional delim = ":") As String|
||Take the last two parts of a delimited string and return them as a new string with the delimiter. Missing parts will be set to zero lenght string|
|log|Sub log(txt As String)|
|||
|LUMP|Function LUMP(account As String, y_year As String) As Double|
||Return the expected lump sum payment for an account based on the prior year's end balance|
|mo_apply|Function mo_apply(start_date As Date, y_year As String, Optional end_mdy As String = "") As Double|
||Get a rational number that represents the number of months that apply in a particular year given the start date and optionally an end date. The end date is a string since there is a bug in the mac excel.. The end date represents the month of the last period to include.  the day is ignored and the last day of the month is used.|
|mo_factor|Function mo_factor(start_date As Date, duration As Double, this_year As Integer) As Double|
||Get a floating point number that represents the number of months that apply in a particular year given the start date and duration|
|ratio_to_start|Function ratio_to_start(account As String, category As String, y_year As String) As Double|
||For investment income and expense, compute the ratio to the start balance, but use the prior end balance since. That should have already been computed.  this allows the table to occur before the balances table in the compute order. To be run in a cell in the invest_iande_work table.|
|RMD_1|Function RMD_1(account As String, account_owner As String, y_year As String, Optional death_year As Integer = 0) As Double|
||Return the req minimum distribution table 1 result for a year for a given account, owner (gbd or vec) and year.. If death year is not given then this function treat this as spousal inheritance. If death year is given the treat this as a beneficiary inheritance|
|sort_tax_table|Function sort_tax_table()|
||Make sure the federal tax tables are sorted properly|
|test_fed_tax|Sub test_fed_tax()|
|||
|test_get_val|Sub test_get_val()|
|||
|test_LUMP|Sub test_LUMP()|
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
