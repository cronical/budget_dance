# VBA Code Summary

|Function or Sub|Signature and info|
|---|---|
|acct_who1|Function acct_who1(acct As String, Optional num_chars As Integer = 1) As String|
||Return the first initial of the owner of an account in format type - who - firm|
|add_wdraw|Function add_wdraw(acct As String, y_year As String) As Variant|
||Get the actual or forecast transfers in (positive) our out(negative). Determines whether the year is actual or forecast, in order to determine the source from the accounts table.. For actuals returns the value from the source table.. For forecast, will add realized gains that are not re-invested. If source table is the retirement table, changes the sign.|
|age_as_of_date|Function age_as_of_date(inits As String, dt As Date) As Double|
||Return the age attained by an account owner in a given year|
|age_of|Function age_of(inits As String, y_year As String) As Integer|
||Return the age attained by an account owner in a given year|
|agg|Function agg(y_year As String, by_tag As Variant, Optional agg_method = "sum", Optional tag_col_name As String = "Tag") As Double|
||Aggregate (default is sum) up the values in the table containing the calling cell for a year where the by_tag is found in the tag column.. Use of this can help avoid the hard coding of addresses into formulas. By default the tag column is "tag" but an alternate can be provided. Other agg_methods are "min" and "max"|
|agg_table|Function agg_table(tbl_name As String, y_year As String, by_tag As String, Optional agg_method = "sum", Optional tag_col_name As String = "Tag") As Double|
||Aggregate (default is sum) up the values in the named table for a year where the by_tag is found in the tag column.. Use of this can help avoid the hard coding of addresses into formulas. By default the tag column is "tag" but an alternate can be provided. Other agg_methods are "min" and "max". A second and third criteria may be provided by extending the by_tag and the tag_col_name as follows:. A delimiter is included in the strings to allow two values to be provided.the delimiter is stile (|). The there should be exactly 0 or 1 or 2 delimiters, andthe by_tag and tag_column_name should agree|
|ANN|Function ANN(account As String, account_owner As String, y_year As String) As Double|
||Deprecated - use annuity instead. Return a year's value for an annuity stream based on the prior year's end balance. Does not properly handle partial years|
|annuity|Function annuity(account As String, y_year As String) As Double|
||Return a year's value for an annuity stream based on the prior year's end balance. Fetches the start date, duration and annual annuity rate from tbl_retir_vals. Rounds to whole number|
|bal_agg|Function bal_agg(y_year As String, val_type As String, Optional acct_type As String = "*", Optional txbl As Integer = 1, Optional active As Integer = 1) As Double|
||Get the sum of values from the balances table for a year and type, optionally further qualified by acct type,taxable status,active status. Wild cards are ok as are excel functions like "<>" prepended to the values for strings. Note all the criteria fields must have values - suggest using na if there is no value such as for an election.|
|calc_retir|Sub calc_retir()|
||Iterate through the years to calc retirement streams based on balances from prior year. Prior balance from balances feeds current retirement, and current invest_iande_work. Retirement feeds aux,. Aux and invest_iande_work feeds current balances. Iande depends on retirement as well and taxes depend on iande|
|calc_table|Sub calc_table()|
||Testing forced calc of table|
|CT_Tax|Function CT_Tax(tax_Year As Integer, taxable_Income As Double) As Double|
||Calculate the ct income tax for a given year and taxable income amount. The so called initial tax calculation only.. Table is not setup exactly like federal - it uses the traditional method not the subraction method.. Gets a result of zero if year not in the table.|
|d2s|Function d2s(dt As Date) As String|
|||
|ei_withhold|Function ei_withhold(legend As String, ei_template, y_year As String) As Double|
||Compute annual social security or medicare withholding for earned income. Relies on naming conventions. Ei_template is a template for the line with earned income.  % is replaced by the person indicator, which. Is the trailing part of the legend.. The legend has two parts separated by hyphen.  the first part is the type of withholding. Which must be either: medicare or soc sec. Y_year is the column heading such as y2022|
|endbal|Function endbal(acct As String, y_year As String) As Variant|
||Compute the end balance for an account for a year|
|extend_iiande|Function extend_iiande(account As String, category As String, y_year As String) As Double|
||For investment income and expense, use a ratio to the start balance to compute a forecast value for the income/expense item on this row. To be run in a cell in the invest_iande_work table.|
|Fed_Tax_CapGn|Function Fed_Tax_CapGn(tax_Year As Integer, taxable_Income As Double, totCapGn As Double) As Double|
||Computes the resulting federal tax with capital gains portion at 15%. The input should include qualified dividends|
|Federal_Tax|Function Federal_Tax(tax_Year As Integer, taxable_Income As Double) As Double|
||Calculate the federal income tax for a given year and taxable income amount. Gets a result of zero if year not in the table.|
|gain|Function gain(acct As String, y_year As String, realized As Boolean) As Variant|
||For bank accounts and investments, return the realized or unrealized gain for an account for a year for actual or forecast. Other types of accounts return zero.. For investments actuals, use the values from invest_actl. For bank account actuals use the row in iande defined by the 'bank_interest' value on the general (state) table|
|get_val|Function get_val(line_key As Variant, tbl_name As String, col_name As String, Optional raise_bad_col = False) As Variant|
||Fetches a value from a given table (it must be an actual worksheet table. If the line is not found in the table, a zero is returned.. Bad columns are usually logged, but if the argument raise_bad_col is true then an error is raised.|
|IntYear|Function IntYear(yval) As Integer|
||Strips off the y on the argument (eg y2019) and returns an integer|
|invest_fees|Function invest_fees(acct As String, y_year As String) As Variant|
||For investments, return the account fees for an account for a year for actual or forecast. Other types of accounts return zero.. For investments actuals, use the values from invest_iande_work|
|is_forecast|Function is_forecast(y_year As String) As Boolean|
||Determine if this year is a forecast year|
|last_two_parts|Function last_two_parts(cat As String, Optional delim = ":") As String|
||Take the last two parts of a delimited string and return them as a new string with the delimiter. Missing parts will be set to zero lenght string|
|linear|Function linear(count As Integer, Optional minimum = 0) As Double|
||Use the excel forecast linear function to extrapolate the value based on the prior <count> values on this line.. Will use <count> number of data points if they exist or fewer if that goes before the first year. The minimum is used to prevent values from going below that amount. Suitable only for year columns.. Due to trouble with the listobject function which makes values empty for cells with formulas, a work around is used. To determine the table name from the worksheet name.this should be ok for major tables which correspond by convention.|
|log|Sub log(txt As String)|
|||
|LUMP|Function LUMP(account As String, y_year As String) As Double|
||Return the expected lump sum payment for an account based on the prior year's end balance|
|MedicarePrem|Function MedicarePrem(b_or_d As Integer, year As String, inflation As Variant, Optional magi As Variant = -1) As Variant|
||Given a year (as y+year), return annual part b premium or part d surcharge (irmaa). Normally look up the modifed adjusted gross from 2 years ago, but if its supplied, like for a test, use that instead.. B_or_d isa 1 for part b premium or 2 for part d surcharge. If the year is not in the table, then the largest year lower than that given will be used. And the resulting value will include inflation.  inflation is given as 1.0x so it can be used directly|
|mo_apply|Function mo_apply(start_date As Date, y_year As String, Optional end_mdy As String = "") As Double|
||Get a rational number that represents the number of months that apply in a particular year given the start date and optionally an end date. The end date is a string since there is a bug in the mac excel.. The end date represents the month of the last period to include.  the day is ignored and the last day of the month is used.|
|nth_word_into|Function nth_word_into(n As Integer, source As String, template As String) As String|
||Insert the nth word (first is 0th) from source into the template, replacing %|
|PartBPrem|Function PartBPrem(year As String, inflation As Variant, Optional magi As Variant = -1) As Variant|
||Given a year (as y+year) and the modifed adjusted gross (2 years ago) return annual part b premium. If the year is not in the table, then the largest year lower than that given will be used. And the resulting value will include inflation.  inflation is given as 1.0x so it can be used directly|
|PartDSurcharge|Function PartDSurcharge(year As String, inflation As Variant, Optional magi As Variant = -1) As Variant|
||Given a year (as y+year) and the modifed adjusted gross (2 years ago) return annual part d surcharge. If the year is not in the table, then the largest year lower than that given will be used. And the resulting value will include inflation.  inflation is given as 1.0x so it can be used directly|
|percent_year_worked|Function percent_year_worked(initials As String) As Double|
||Using the year of the current column and the data in the people table, return a number between 0 and 1. Indicating the percent of the year worked for the person with initials given|
|prior_value|Function prior_value(line As String) As Variant|
||Get the prior years' value for this line. suitable only for year columns.|
|ratio_to_start|Function ratio_to_start(account As String, category As String, y_year As String) As Double|
||For investment income and expense, compute the ratio to the start balance, but use the prior end balance since. That should have already been computed.  this allows the table to occur before the balances table in the compute order. To be run in a cell in the invest_iande_work table.|
|reinv_amt|Function reinv_amt(acct_name As String, y_year As String) As Double|
||Compute the reinvestment amount for an account and year.|
|retir_parm|Function retir_parm(code As String, who As String) As Variant|
||Get a retirement paramenter given code and code (g or v)|
|RMD_1|Function RMD_1(account As String, account_owner As String, y_year As String, Optional death_year As Integer = 0) As Double|
||Return the req minimum distribution table 1 result for a year for a given account, owner (gbd or vec) and year.. If death year is not given then this function treat this as spousal inheritance. If death year is given the treat this as a beneficiary inheritance|
|rolling_avg|Function rolling_avg(Optional max_value As Variant = Null, Optional lookback As Integer = 5, Optional table As String = "", Optional key As String = "", Optional this_y_year As String = "") As Double|
||Look back at previous columns and average the numeric values found there, ignoring items before 2018, but including zeros. Max_value if provided is used instead of any higher values. Lookback is defaulted to 5 years. If not provided, table, key and y_year are taken from the calling cell. Return the average.  returns 0 if the count of valid items is 0.|
|simple_return|Function simple_return(account As String, y_year As String) As Double|
||Return the rlzd gain divided by the average of the start and end balances (or zero)|
|sort_tax_table|Function sort_tax_table()|
||Make sure the federal tax tables are sorted properly|
|test_fed_tax|Sub test_fed_tax()|
|||
|test_get_val|Sub test_get_val()|
|||
|test_LUMP|Sub test_LUMP()|
|||
|test_medicarePrem|Sub test_medicarePrem()|
|||
|test_mo_apply|Sub test_mo_apply()|
|||
|test_nth|Sub test_nth()|
|||
|test_sort|Sub test_sort()|
|||
|this_col_name|Function this_col_name() As String|
||Return the caller's column name, assuming the cell is in a table.. Otherwise generates a #value  error. Use to make formulas more portable|
|unrlz|Function unrlz(acct As String, y_year As String) As Variant|
||Compute the unrealized gain or loss for an account for a year, assuming end bal is fixed|
|ws_for_table_name|Function ws_for_table_name(tbl_name As String) As String|
||Find out what worksheet the named table occurs on|
|y_offset|Function y_offset(y_year As String, offset As Integer) As String|
||Given a y_year offset it by the amount given, producing a new y_year|
