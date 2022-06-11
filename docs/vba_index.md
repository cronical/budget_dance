# VBA Code Summary

|Function or Sub|Signature and info|
|---|---|
|acct_who1|Function acct_who1(acct As String) As String|
||return the first initial of the owner of an account in format type - who - firm|
|add_wdraw|Function add_wdraw(acct As String, y_year As String, Optional is_fcst As Boolean = False) As Variant|
||grab the actual transfers in (positive) our out(negative)|
||ignoring the optional is_fcst argument - instead: compute it|
|age_of|Function age_of(inits As String, y_year As String) As Integer|
||return the age attained by GBD or VEC in a given year|
|ANN|Function ANN(account As String, account_owner As String, y_year As String) As Double|
||return a year's value for an annuity stream based on the prior year's end balance|
||does not properly handle partial years|
|calc_retir|Sub calc_retir()|
||iterate through the years to calc retirement streams based on balances from prior year|
||prior balance from balances feeds current retirement, which feeds aux, which feeds current balances|
||iande depends on retirement as well and taxes depend on iande|
|d2s|Function d2s(dt As Date) As String|
|endbal|Function endbal(acct As String, y_year As String) As Variant|
||compute the end balance for an account for a year|
|Fed_Tax_CapGn|Function Fed_Tax_CapGn(tax_Year As Integer, taxable_Income As Double, totCapGn As Double) As Double|
||computes the resulting federal tax with capital gains portion at 15%|
||the input should include qualified dividends|
|Federal_Tax|Function Federal_Tax(tax_Year As Integer, taxable_Income As Double) As Double|
||Calculate the federal income tax for a given year and taxable income amount|
||gets a result of zero if year not in the table.|
|gain|Function gain(acct As String, y_year As String, realized As Boolean) As Variant|
||work out an esitmate of the realized or unrealized gain for an account for a year for forecast|
||for actual, use the values from invest_actl|
|get_val|Function get_val(line_key As Variant, tbl_name As String, col_name As String) As Variant|
||Fetches a value from a given table (it must be an actual worksheet table|
||If the line is not found in the table, a zero is returned.|
|IntYear|Function IntYear(yval) As Integer|
||strips off the Y on the argument (eg Y2019) and returns an integer|
|is_forecast|Function is_forecast(y_year As String) As Boolean|
||determine if this year is a forecast year|
|log|Sub log(txt As String)|
|LUMP|Function LUMP(account As String, y_year As String) As Double|
||return the expected lump sum payment for an account based on the prior year's end balance + any items in the aux table|
||for the current year (items that begin with the account name)|
|MedicarePrem|Function MedicarePrem(bord As Integer, year As String, magi As Variant, inflation As Variant) As Variant|
||Given a year (as Y+year) and the modifed adjusted gross (2 years ago) return annual part b premium or part D surcharge (IRMAA)|
||bord isa 1 for part B premium or 2 for Part D surcharge|
||If the year is not in the table, then the largest year lower than that given will be used|
||and the resulting value will include inflation.  Inflation is given as 1.0x so it can be used directly|
|mo_apply|Function mo_apply(start_date As Date, y_year As String, Optional end_mdy As String = "") As Double|
||Get a rational number that represents the number of months that apply in a particular year given the start date and optionally an end date|
||The end date is a string since there is a bug in the Mac Excel.|
||The end date represents the month of the last period to include.  The day is ignored and the last day of the month is used.|
|PartBPrem|Function PartBPrem(year As String, magi As Variant, inflation As Variant) As Variant|
||Given a year (as Y+year) and the modifed adjusted gross (2 years ago) return annual part b premium|
||If the year is not in the table, then the largest year lower than that given will be used|
||and the resulting value will include inflation.  Inflation is given as 1.0x so it can be used directly|
|PartDSurcharge|Function PartDSurcharge(year As String, magi As Variant, inflation As Variant) As Variant|
||Given a year (as Y+year) and the modifed adjusted gross (2 years ago) return annual part D surcharge|
||If the year is not in the table, then the largest year lower than that given will be used|
||and the resulting value will include inflation.  Inflation is given as 1.0x so it can be used directly|
|retir_med|Function retir_med(who1 As String, y_year As String) As Double|
||return the forecast medical expenses including premium and deductible for person with initial who1 given a year|
|retir_parm|Function retir_parm(code As String, who As String) As Variant|
||Get a retirement paramenter given code and code (G or V)|
|RMD_1|Function RMD_1(account As String, account_owner As String, y_year As String, Optional death_year As Integer = 0) As Double|
||return the req minimum distribution table 1 result for a year for a given account, owner (GBD or VEC) and year.|
||if death year is not given then this function treat this as spousal inheritance|
||if death year is given the treat this as a beneficiary inheritance|
|sort_tax_table|Function sort_tax_table()|
||make sure the federal tax tables are sorted properly|
|test_fed_tax|Sub test_fed_tax()|
|test_get_val|Sub test_get_val()|
|test_LUMP|Sub test_LUMP()|
|test_medicarePrem|Sub test_medicarePrem()|
|test_mo_apply|Sub test_mo_apply()|
|test_retir_med|Sub test_retir_med()|
|test_sort|Sub test_sort()|
|unrlz|Function unrlz(acct As String, y_year As String) As Variant|
||compute the unrealized gain or loss for an account for a year, assuming end bal is fixed|
|ws_for_table_name|Function ws_for_table_name(tbl_name As String) As String|
||find out what worksheet the named table occurs on|
