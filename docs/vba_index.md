# VBA Code Summary

|Function or Sub|Signature and info|
|---|---|
|acct_who1|Function acct_who1(acct As String) As String|
||Return the first initial of the owner of an account in format type - who - firm|
|add_wdraw|Function add_wdraw(acct As String, y_year As String, Optional is_fcst As Boolean = False) As Variant|
||Grab the actual transfers in (positive) our out(negative). Ignoring the optional is_fcst argument - instead: compute it|
|age_of|Function age_of(inits As String, y_year As String) As Integer|
||Return the age attained by an account owner in a given year|
|ANN|Function ANN(account As String, account_owner As String, y_year As String) As Double|
||Return a year's value for an annuity stream based on the prior year's end balance. Does not properly handle partial years|
|calc_retir|Sub calc_retir()|
||Iterate through the years to calc retirement streams based on balances from prior year. Prior balance from balances feeds current retirement, which feeds aux, which feeds current balances. Iande depends on retirement as well and taxes depend on iande|
|calc_table|Sub calc_table()|
||Testing forced calc of table|
|d2s|Function d2s(dt As Date) As String|
|||
|endbal|Function endbal(acct As String, y_year As String) As Variant|
||Compute the end balance for an account for a year|
|Fed_Tax_CapGn|Function Fed_Tax_CapGn(tax_Year As Integer, taxable_Income As Double, totCapGn As Double) As Double|
||Computes the resulting federal tax with capital gains portion at 15%. The input should include qualified dividends|
|Federal_Tax|Function Federal_Tax(tax_Year As Integer, taxable_Income As Double) As Double|
||Calculate the federal income tax for a given year and taxable income amount. Gets a result of zero if year not in the table.|
|gain|Function gain(acct As String, y_year As String, realized As Boolean) As Variant|
||For bank accounts and investments, return the realized or unrealized gain for an account for a year for actual or forecast. Other types of accounts return zero.. For investments actuals, use the values from invest_actl. For bank account actuals use the row in iande defined by the 'bank_interest' value on the general (state) table|
|get_val|Function get_val(line_key As Variant, tbl_name As String, col_name As String) As Variant|
||Fetches a value from a given table (it must be an actual worksheet table. If the line is not found in the table, a zero is returned.|
|IntYear|Function IntYear(yval) As Integer|
||Strips off the y on the argument (eg y2019) and returns an integer|
|is_forecast|Function is_forecast(y_year As String) As Boolean|
||Determine if this year is a forecast year|
|log|Sub log(txt As String)|
|||
|LUMP|Function LUMP(account As String, y_year As String) As Double|
||Return the expected lump sum payment for an account based on the prior year's end balance + any items in the aux table. For the current year (items that begin with the account name)|
|MedicarePrem|Function MedicarePrem(bord As Integer, year As String, magi As Variant, inflation As Variant) As Variant|
||Given a year (as y+year) and the modifed adjusted gross (2 years ago) return annual part b premium or part d surcharge (irmaa). Bord isa 1 for part b premium or 2 for part d surcharge. If the year is not in the table, then the largest year lower than that given will be used. And the resulting value will include inflation.  inflation is given as 1.0x so it can be used directly|
|mo_apply|Function mo_apply(start_date As Date, y_year As String, Optional end_mdy As String = "") As Double|
||Get a rational number that represents the number of months that apply in a particular year given the start date and optionally an end date. The end date is a string since there is a bug in the mac excel.. The end date represents the month of the last period to include.  the day is ignored and the last day of the month is used.|
|PartBPrem|Function PartBPrem(year As String, magi As Variant, inflation As Variant) As Variant|
||Given a year (as y+year) and the modifed adjusted gross (2 years ago) return annual part b premium. If the year is not in the table, then the largest year lower than that given will be used. And the resulting value will include inflation.  inflation is given as 1.0x so it can be used directly|
|PartDSurcharge|Function PartDSurcharge(year As String, magi As Variant, inflation As Variant) As Variant|
||Given a year (as y+year) and the modifed adjusted gross (2 years ago) return annual part d surcharge. If the year is not in the table, then the largest year lower than that given will be used. And the resulting value will include inflation.  inflation is given as 1.0x so it can be used directly|
|retir_med|Function retir_med(who1 As String, y_year As String) As Double|
||Return the forecast medical expenses including premium and deductible for person with initial who1 given a year|
|retir_parm|Function retir_parm(code As String, who As String) As Variant|
||Get a retirement paramenter given code and code (g or v)|
|RMD_1|Function RMD_1(account As String, account_owner As String, y_year As String, Optional death_year As Integer = 0) As Double|
||Return the req minimum distribution table 1 result for a year for a given account, owner (gbd or vec) and year.. If death year is not given then this function treat this as spousal inheritance. If death year is given the treat this as a beneficiary inheritance|
|rolling_avg|Function rolling_avg(table As String, key As String, this_y_year As String, lookback As Integer) As Double|
||Look back at previous columns and average the numeric values found there, ignoring non-numerics. Return the average|
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
|test_retir_med|Sub test_retir_med()|
|||
|test_sort|Sub test_sort()|
|||
|unrlz|Function unrlz(acct As String, y_year As String) As Variant|
||Compute the unrealized gain or loss for an account for a year, assuming end bal is fixed|
|ws_for_table_name|Function ws_for_table_name(tbl_name As String) As String|
||Find out what worksheet the named table occurs on|
