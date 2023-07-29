# VBA Code
``` vbscript
Attribute VB_Name = "Module1"

Public Const dbg As Boolean = False
Option Base 0

Function acct_who1(acct As String, Optional num_chars As Integer = 1) As String
'return the first initial of the owner of an account in format type - who - firm
    Dim parts() As String
    parts = Split(acct, " - ")
    who = parts(1)
    acct_who1 = Left(who, num_chars)
End Function

Function age_as_of_date(inits As String, dt As Date) As Double
'return the age attained by an account owner in a given year
'deprecation candidate - appears not to be used
    Dim dob As Date, eoy As Date
    Dim diff As Double, age As Double
    dob = get_val(inits, "tbl_people", "DOB")
    diff = (dt - dob) / 365.25
    age = Application.WorksheetFunction.Round(diff, 3)
    age_as_of_date = age
End Function

Function age_of(inits As String, y_year As String) As Integer
'return the age attained by an account owner in a given year
    Dim dob As Date, eoy As Date
    Dim diff As Double, age As Integer
    dob = get_val(inits, "tbl_people", "DOB")
    eoy = DateSerial(IntYear(y_year), 12, 31)
    diff = (eoy - dob) / 365.25
    age = Int(Application.WorksheetFunction.RoundDown(diff, 0))
    age_of = age
End Function

Function agg(y_year As String, by_tag As Variant, Optional agg_method = "sum", Optional tag_col_name As String = "Tag") As Double
' Aggregate (default is sum) up the values in the table containing the calling cell for a year where the by_tag is found in the tag column.
' Use of this can help avoid the hard coding of addresses into formulas
' By default the tag column is "tag" but an alternate can be provided
' Other agg_methods are "min" and "max"
    Dim agg_val As Double
    
    Dim tbl As ListObject
    Dim point As Range, val_rng As Range, tag_col As Range
    Set point = Application.caller
    Set tbl = point.ListObject
    Set tag_rng = tbl.ListColumns(tag_col_name).Range
    Set val_rng = tbl.ListColumns(y_year).Range
    Select Case agg_method
    Case "sum"
        agg_val = Application.WorksheetFunction.SumIfs(val_rng, tag_rng, by_tag)
    Case "min"
        agg_val = Application.WorksheetFunction.MinIfs(val_rng, tag_rng, by_tag)
    Case "max"
        agg_val = Application.WorksheetFunction.MaxIfs(val_rng, tag_rng, by_tag)
    End Select
    agg = agg_val
End Function

Function agg_table(tbl_name As String, y_year As String, by_tag As String, Optional agg_method = "sum", Optional tag_col_name As String = "Tag") As Double
' Aggregate (default is sum) up the values in the named table for a year where the by_tag is found in the tag column.
' Use of this can help avoid the hard coding of addresses into formulas
' By default the tag column is "tag" but an alternate can be provided
' Other agg_methods are "min" and "max"
' A second and third criteria may be provided by extending the by_tag and the tag_col_name as follows:
'  A delimiter is included in the strings to allow two values to be provided.The delimiter is stile (|)
'  The there should be exactly 0 or 1 or 2 delimiters, andthe by_tag and tag_column_name should agree
    Dim agg_val As Double
    Dim tbl As ListObject
    Dim point As Range, val_rng As Range, tag_rngs() As Range
    Dim by_tags() As String, tag_col_names() As String, by_tags_v As Variant
    
    On Error GoTo ErrHandler
    delim = "|"
    by_tags = Split(by_tag, delim)
    tag_col_names = Split(tag_col_name, delim)
    
    Set point = Application.caller
    ws_name = ws_for_table_name(tbl_name)
    Set tbl = ThisWorkbook.Worksheets(ws_name).ListObjects(tbl_name)
    Set val_rng = tbl.ListColumns(y_year).Range
    ReDim tag_rngs(UBound(by_tags))
    ReDim by_tags_v(UBound(by_tags))
    

    For i = LBound(by_tags) To UBound(by_tags)
        Set tag_rngs(i) = tbl.ListColumns(tag_col_names(i)).Range
        If IsNumeric(by_tags(i)) Then
            by_tags_v(i) = CInt(by_tags(i))
        Else
            by_tags_v(i) = by_tags(i)
        End If
    Next i
    
    Select Case agg_method
    Case "sum"
        Select Case UBound(by_tags)
        Case 0
            agg_val = Application.WorksheetFunction.SumIfs(val_rng, tag_rngs(0), by_tags_v(0))
        Case 1
            agg_val = Application.WorksheetFunction.SumIfs(val_rng, tag_rngs(0), by_tags_v(0), tag_rngs(1), by_tags_v(1))
        Case 2
            agg_val = Application.WorksheetFunction.SumIfs(val_rng, tag_rngs(0), by_tags_v(0), tag_rngs(1), by_tags_v(1), tag_rngs(2), by_tags_v(2))
        End Select
    Case "min"
        agg_val = Application.WorksheetFunction.MinIfs(val_rng, tag_rngs(0), by_tags(0))
    Case "max"
        agg_val = Application.WorksheetFunction.MaxIfs(val_rng, tag_rngs(0), by_tags(0))
    End Select
    agg_table = agg_val
    Exit Function
ErrHandler:
    log ("[ " & point.address & " ] agg_table: " & Err.Number & " " & Err.Description)
End Function

Function ANN(anny_start As Date, duration As Integer, anny_rate As Double, prior_end_bal As Double, this_year As Integer, month_factor As Double) As Double
'return a year's value for an annuity stream based on the prior year's end balance
'this version leaves all the Excel dependencies visible to Excel
    Dim months, nper, sm, sy As Integer
    ANN = 0
    If month_factor > 0 Then
        ' TODO in final period just take the whole amount?
        sm = Month(anny_start)
        sy = year(anny_start)
        If sy = this_year Then
            nper = 12 * duration
        End If
        If sy < this_year Then
            nper = (12 * duration) - ((13 - sm) + 12 * (-1 + (this_year - sy)))
        End If
        If sy > this_year Then
            nper = 0
        End If
        ' nper is now number of months remaining
        If nper > 0 Then
            result = -Application.WorksheetFunction.Pmt(anny_rate, nper / 12, prior_end_bal)
            result = Application.WorksheetFunction.Round(result, 0)
            ANN = result
        End If
    End If

End Function

Function annuity(account As String, y_year As String) As Double
'return a year's value for an annuity stream based on the prior year's end balance
'fetches the start date, duration and annual annuity rate from tbl_retir_vals
'rounds to whole number
    Dim anny_start As Date
    Dim duration As Integer, this_year As Integer
    Dim annual_rate As Double, anny_rate As Double
    this_year = IntYear(y_year)
    prior_end_bal = get_val("End Bal" & account, "tbl_balances", "Y" & this_year - 1)
    anny_start = get_val(account, "tbl_retir_vals", "Start Date")
    duration = get_val(account, "tbl_retir_vals", "Anny Dur Yrs")
    anny_rate = get_val(account, "tbl_retir_vals", "Anny Rate")
    
    n = duration - (this_year - year(anny_start))
    result = 0
    If n > 0 Then
        result = -Application.WorksheetFunction.Pmt(anny_rate, n, prior_end_bal)
        factor = mo_apply(anny_start, y_year) ' TODO put end date on this call
        result = factor * result
        result = Application.WorksheetFunction.Round(result, 0)
    End If
    annuity = result
End Function

Function bal_agg(y_year As String, val_type As String, Optional acct_type As String = "*", Optional txbl As Integer = 1, Optional active As Integer = 1) As Double
'get the sum of values from the balances table for a year and type, optionally further qualified by acct type,taxable status,active status
'wild cards are OK as are Excel functions like "<>" prepended to the values for strings
'NOTE all the criteria fields must have values - suggest using NA if there is no value such as for an election.

    Dim this_year As Integer, tbl_name As String
    Dim result As Double
    Dim tbl As ListObject, crit_col1 As ListColumn, crit_col2 As ListColumn, val_col As ListColumn
    Dim criteria1 As String, criteria2 As String
    
    tbl_name = "tbl_balances"
    ws_name = ws_for_table_name(tbl_name)
    Set tbl = ThisWorkbook.Worksheets(ws_name).ListObjects(tbl_name)
    Set crit_col1 = tbl.ListColumns("ValType")
    Set crit_col2 = tbl.ListColumns("Type")
    Set crit_col3 = tbl.ListColumns("Income Txbl")
    Set crit_col4 = tbl.ListColumns("Active")
    Set val_col = tbl.ListColumns(y_year)
    result = Application.WorksheetFunction.SumIfs(val_col.Range, _
        crit_col1.Range, val_type, _
        crit_col2.Range, acct_type, _
        crit_col3.Range, txbl, _
        crit_col4.Range, active)
    bal_agg = result

End Function

Sub calc_retir()
'iterate through the years to calc retirement streams based on balances from prior year
'prior balance from balances feeds current retirement, and current invest_iande_work
'retirement feeds aux,
'aux and invest_iande_work feeds current balances
'iande depends on retirement as well and taxes depend on iande
    Dim rcols As Range, rcell As Range, single_cell As Range
    Dim tbls() As ListObject
    Dim tbl_names() As String, ws_names() As String
    Dim msg As String, formula As String
    log ("-----------------------------")
    log ("Entering manual calculation mode.")
    Application.Calculation = xlCalculationManual
    
    tbl_names = Split("tbl_retir_vals;tbl_aux;tbl_invest_iande_work;tbl_balances;tbl_iande;tbl_taxes", ";")
    k = UBound(tbl_names)
    ReDim tbls(k), ws_names(k)
    msg = ""
    For i = LBound(tbl_names) To k
        ws_names(i) = ws_for_table_name(tbl_names(i))
        Set tbls(i) = ThisWorkbook.Worksheets(ws_names(i)).ListObjects(tbl_names(i))
        If Len(msg) > 0 Then msg = msg & ","
        If i = UBound(tbl_names) Then msg = msg & " and "
        msg = msg & ws_names(i)
        
    Next i
    
    Set rcols = tbls(0).HeaderRowRange
    Set col = tbls(0).ListColumns("yearly")
    col.Range.Dirty
    col.Range.Calculate
    log ("Retirement yearly column refreshed.")
    
    For Each rcell In rcols
        If InStr(rcell.value, "Y20") = 1 Then
            log ("Calculating for " & rcell.value)
            For i = LBound(tbls) To UBound(tbls)
                Set col = tbls(i).ListColumns(rcell.value)
                t_name = tbls(i).Name
                Application.StatusBar = rcell.value & ":" & t_name
                log ("  " & t_name & " - Range " & col.Range.address)
                If dbg Then
                    For Each single_cell In col.Range.Cells
                        formula = single_cell.formula
                        If 0 < Len(formula) Then
                            If Left(formula, 1) = "=" Then
                            log ("    " & single_cell.address & ":    " & formula)
                                single_cell.Dirty
                                single_cell.Calculate
                            End If
                        End If
                        Next
                Else
                    col.Range.Dirty
                    col.Range.Calculate
                End If
            Next i

         End If
    Next rcell
    log ("Entering automatic calculation mode.")
    Application.StatusBar = ""
    log ("-----------------------------")
    Application.Calculation = xlCalculationAutomatic

End Sub

Sub calc_table()
'Testing forced calc of table
    Dim rcols As Range, rcell As Range
    Dim tbl As ListObject
    Dim tbl_name As String
    Dim ws_name As String
    Dim msg As String
    log ("-----------------------------")
    log ("Entering manual calculation mode.")
    Application.Calculation = xlCalculationManual
    tbl_name = "tbl_balances"
    ws_name = ws_for_table_name(tbl_name)
    Set tbl = ThisWorkbook.Worksheets(ws_name).ListObjects(tbl_name)

    
    tbl.Range.Dirty
    tbl.Range.Calculate
    log (tbl_name & " refreshed.")
    log ("Entering automatic calculation mode.")
    log ("-----------------------------")
    Application.Calculation = xlCalculationAutomatic

End Sub

Function CT_Tax(tax_Year As Integer, taxable_Income As Double) As Double
'Calculate the CT income tax for a given year and taxable income amount
'The so called Initial Tax Calculation only.
'Table is not setup exactly like Federal - it uses the traditional method not the subraction method.
'gets a result of zero if year not in the table.
    Dim result As Double
    Dim tbl_name As String
    Dim tbl As ListObject
    Dim lr As ListRow
    Dim rng As Range
    Dim yr As Integer
    Dim ti As Double, rt As Double, base As Double
    
    tbl_name = "tbl_ct_tax"
    ws = ws_for_table_name(tbl_name)
    Set tbl = ThisWorkbook.Worksheets(ws).ListObjects(tbl_name)
    result = 0
    prior = 0
    For Each lr In tbl.ListRows()
        Set rng = lr.Range
        yr = rng.Cells(1, 1).value
        ti = rng.Cells(1, 2).value
        rt = rng.Cells(1, 3).value
        base = rng.Cells(1, 4).value
        If tax_Year = yr Then
            If taxable_Income < ti And taxable_Income >= prior Then
                result = base + (rt * (taxable_Income - prior))
                result = Round(result, 0)
            End If
            prior = ti
        End If
    Next lr
    CT_Tax = result
End Function

Function CT_Tax_Range(ParamArray parms() As Variant) As Double
'Pass in either
'  a single range of two values to get CT initial tax; or
'  a list of ranges of single values - count of 2
'Encapsulates CT_tax
'First value is tax table year as integer
'Second value is CT taxable income


Dim args As Variant
Dim vals As Variant
Dim i As Integer
Dim rng As Range

n = UBound(parms)

vals = Array(0, 0)
If n = 0 Then
    Set rng = parms(0)
    args = rng.value
    For i = LBound(args, 1) To UBound(args, 1)
        vals(i - 1) = args(i, 1)
    Next i
Else
    For i = LBound(parms) To n
        Set rng = parms(i)
        vals(i) = rng.value
    Next i
End If
result = CT_Tax(CInt(vals(0)), CDbl(vals(1)))

CT_Tax_Range = result

End Function

Function d2s(dt As Date) As String
    d2s = Format(dt, "mm/dd/yyyy")
End Function

Function Fed_Tax_CapGn(tax_Year As Integer, taxable_Income As Double, totCapGn As Double) As Double
'computes the resulting federal tax with capital gains portion at 15%
'the input should include qualified dividends

    Dim base As Double, result As Double, cgt As Double
    base = Federal_Tax(tax_Year, taxable_Income - totCapGn)
    cgt = 0.15 * totCapGn
    result = base + cgt
    Fed_Tax_CapGn = result
    
End Function

Function Fed_Tax_Range(ParamArray parms() As Variant) As Double
'Pass in either
'  a single range of two or three values to get federal tax; or
'  a list of ranges of single values - either 2 or 3
'Encapsulates Fed_Tax_CapGn
'First value is tax table year as integer
'Second value is taxable income
'Third is the capital gains
'If the 3rd value is zero then returns the federal tax without adjusting for capital gains


Dim args As Variant
Dim vals As Variant
Dim i As Integer
Dim rng As Range

n = UBound(parms)

vals = Array(0, 0, 0)
If n = 0 Then
    Set rng = parms(0)
    args = rng.value
    For i = LBound(args, 1) To UBound(args, 1)
        vals(i - 1) = args(i, 1)
    Next i
Else
    For i = LBound(parms) To n
        Set rng = parms(i)
        vals(i) = rng.value
    Next i
End If
result = Fed_Tax_CapGn(CInt(vals(0)), CDbl(vals(1)), CDbl(vals(2)))

Fed_Tax_Range = result

End Function

Function Federal_Tax(tax_Year As Integer, taxable_Income As Double) As Double
'Calculate the federal income tax for a given year and taxable income amount
'gets a result of zero if year not in the table.
    Dim result As Double
    Dim tbl_name As String
    Dim tbl As ListObject
    Dim lr As ListRow
    Dim rng As Range
    Dim yr As Integer
    Dim ti As Double
    Dim rt As Double
    Dim sb As Double
    
    tbl_name = "tbl_fed_tax"
    ws = ws_for_table_name(tbl_name)
    Set tbl = ThisWorkbook.Worksheets(ws).ListObjects(tbl_name)
    result = 0
    For Each lr In tbl.ListRows()
        Set rng = lr.Range
        yr = rng.Cells(1, 1).value
        ti = rng.Cells(1, 2).value
        rt = rng.Cells(1, 3).value
        sb = rng.Cells(1, 4).value
        If tax_Year = yr Then
            If taxable_Income > ti Then
                result = (rt * taxable_Income) - sb
                result = Round(result, 0)
            End If
        End If
    Next lr
    Federal_Tax = result
End Function

Function get_val(line_key As Variant, tbl_name As String, col_name As String, Optional raise_bad_col = False) As Variant
'Fetches a value from a given table (it must be an actual worksheet table
'If the line is not found in the table, a zero is returned.
'Bad columns are usually logged, but if the argument raise_bad_col is True then an error is raised.
 
    Dim value As Variant, rng As Variant
    Dim caller As Range
    Dim address As String
    address = "no addr"
    On Error GoTo skip ' allow testing from outside of Excel
    Set caller = Application.caller()
    address = caller.Worksheet.Name & "!" & caller(1, 1).address
skip:
    ws = ws_for_table_name(tbl_name)
    
    'now get the data
    With ThisWorkbook.Worksheets(ws)
        Set rng = .ListObjects(tbl_name).HeaderRowRange
        Dim cr As Range

        On Error GoTo ErrHandler1
        col = Application.WorksheetFunction.Match(col_name, rng, False)
        Set rng = .ListObjects(tbl_name).DataBodyRange
        On Error GoTo ErrHandler
        value = Application.WorksheetFunction.VLookup(line_key, rng, col, False)
        If IsEmpty(value) Then
            value = 0
        End If
    
    End With
    get_val = value
    Exit Function
    
ErrHandler:
    log ("[" & address & " ] get_val: " & line_key & " not found in " & tbl_name & ", using zero as value for " & col_name)
    Dim lkRange As Range
    If False Then 'use this to debug missing lines. e.g. tbl_name = "tbl_taxes" Then
        Set lkRange = ThisWorkbook.Worksheets(ws).ListObjects(tbl_name).ListColumns(1).DataBodyRange
        Debug.Print (lkRange.count)
        For Each c In lkRange.Cells
            log (c.value)
        Next
    End If
    get_val = 0
    Exit Function
ErrHandler1:
    If raise_bad_col = True Then
        Err.Raise vbObjectError + 1729, , "Bad column: " + col_name
    
    End If
    log ("[ " & address & " ] get_val: " & Err.Number & " " & Err.Description)
    log ("Trying to locate column: " & col_name & " in table " & tbl_name)
    log ("line is " & line_key)
End Function

Function IntYear(yval) As Integer
'strips off the Y on the argument (eg Y2019) and returns an integer
    y = 0 + Right(yval, 4)
    IntYear = y
End Function

Function is_forecast(y_year As String) As Boolean
'determine if this year is a forecast year
    ffys = get_val("first_forecast", "tbl_gen_state", "Value")
    ffy = IntYear(ffys)
    ty = IntYear(y_year)
    r = ty >= ffy
    is_forecast = r
End Function

Function last_two_parts(cat As String, Optional delim = ":") As String
'take the last two parts of a delimited string and return them as a new string with the delimiter
'missing parts will be set to zero lenght string
    Dim arr() As String
    arr = Split("::" + cat, delim)
    k = UBound(arr)
    r = arr(k - 1) + ":" + arr(k)
    last_two_parts = r
End Function

Sub log(txt As String)
    fn = ThisWorkbook.Path & "/fcast_log.txt"
    Open ThisWorkbook.Path & "/log.txt" For Append As #1
    Print #1, (Format(Now, "mm/dd/yyyy HH:mm:ss: ") & txt)
    Close #1
End Sub

Function LUMP(account As String, y_year As String) As Double
'return the expected lump sum payment for an account based on the prior year's end balance
    Dim this_year As Integer, tbl_name As String
    Dim prior_end_bal As Double
    prior_end_bal = get_val("End Bal" & account, "tbl_balances", y_offset(y_year, -1))
    LUMP = prior_end
End Function

Function MedicarePrem(b_or_d As Integer, year As String, inflation As Variant, Optional magi As Variant = -1) As Variant
'Given a year (as Y+year), return annual part b premium or part D surcharge (IRMAA)
'normally look up the modifed adjusted gross from 2 years ago, but if its supplied, like for a test, use that instead.
'b_or_d isa 1 for part B premium or 2 for Part D surcharge
'If the year is not in the table, then the largest year lower than that given will be used
'and the resulting value will include inflation.  Inflation is given as 1.0x so it can be used directly
    Dim yr As Integer
    Dim tbl_name As String, ws_name As String, magi_yr As String
    Dim tbl As ListObject
    Dim lr As ListRow, rng As Range
    Dim infl As Variant
    
    yr = IntYear(year)
    If magi = -1 Then
        magi_yr = y_offset(year, -2)
        magi = get_val("Adjusted gross - TOTAL", "tbl_taxes", magi_yr)
    End If
    magi = Application.WorksheetFunction.Max(1, magi)
    tbl_name = "tbl_part_b"
    ws_name = ws_for_table_name(tbl_name)
    Set tbl = ThisWorkbook.Worksheets(ws_name).ListObjects(tbl_name)
    Set yr_col = tbl.ListColumns("year")
    y = Application.WorksheetFunction.VLookup(yr, yr_col.Range, 1, True) ' latest year for which we have data
    MedicarePrem = 0 'in case the if never succeeds
    For Each lr In tbl.ListRows()
        Set rng = lr.Range
        ry = rng.Cells(1, 1).value
        rl = rng.Cells(1, 2).value
        rh = rng.Cells(1, 3).value
        valu = rng.Cells(1, 3 + b_or_d).value
        pw = (yr - y)
        If (ry = y And rl < magi And rh >= magi) Then
            p = valu * 12
            infl = CDbl(Application.WorksheetFunction.Power(inflation, pw))
            MedicarePrem = p * infl
            Exit For
        End If
    Next
End Function

Function mo_apply(start_date As Date, y_year As String, Optional end_mdy As String = "") As Double
'Get a rational number that represents the number of months that apply in a particular year given the start date and optionally an end date
'The end date is a string since there is a bug in the Mac Excel.
'The end date represents the month of the last period to include.  The day is ignored and the last day of the month is used.
    Dim result As Double, distance As Double, sign As Integer, months As Integer
    Dim ed As Date, sd As Date
    If end_mdy = "" Then
        ed = DateSerial(3000, 12, 31) 'the default since the literal is not working on MacExcel
    Else
        mdy = Split(end_mdy, "/")
        ed = DateSerial(mdy(2), mdy(0) + 1, 1) - 1
    End If
    ed = Application.WorksheetFunction.Min(ed, DateSerial(IntYear(y_year), 12, 31))
    sd = Application.WorksheetFunction.Max(start_date, DateSerial(IntYear(y_year), 1, 1))
    distance = (ed - sd) / (365.25 / 12)
    months = Round(distance, 0)
    months = Application.WorksheetFunction.Min(12, months)
    months = Application.WorksheetFunction.Max(0, months)
    result = months / 12
    mo_apply = result
End Function

Function mo_factor(start_date As Date, duration As Double, this_year As Integer) As Double
'Get a floating point number that represents the number of months that apply in a particular year given the start date and duration
    mo_factor = 0#
    If this_year = year(start_date) Then
        mo_factor = (12 - (Month(start_date) - 1)) / 12
    ElseIf this_year > year(start_date) Then
        If this_year <= year(start_date + 365.25 * duration) Then
            mo_factor = 1#  'In the last period we take whatever is left, not a portion of it.
        End If
    End If
End Function

Function PartBPrem(year As String, inflation As Variant, Optional magi As Variant = -1) As Variant
'Given a year (as Y+year) and the modifed adjusted gross (2 years ago) return annual part b premium
'If the year is not in the table, then the largest year lower than that given will be used
'and the resulting value will include inflation.  Inflation is given as 1.0x so it can be used directly
    PartBPrem = MedicarePrem(1, year, inflation, magi)
End Function

Function PartDSurcharge(year As String, inflation As Variant, Optional magi As Variant = -1) As Variant
'Given a year (as Y+year) and the modifed adjusted gross (2 years ago) return annual part D surcharge
'If the year is not in the table, then the largest year lower than that given will be used
'and the resulting value will include inflation.  Inflation is given as 1.0x so it can be used directly
    PartDSurcharge = MedicarePrem(2, year, inflation, magi)
End Function

Function percent_year_worked(initials As String) As Double
'Using the year of the current column and the data in the people table, return a number between 0 and 1
'indicating the percent of the year worked for the person with initials given
    Dim result As Double
    Dim retir_date As Date
    result = 0
    retir_date = get_val(initials, "tbl_people", "Retire Date")
    y_year = this_col_name()
    y = IntYear(y_year)
    j1 = DateSerial(y, 1, 1)
    diff = DateDiff("d", j1, retir_date)
    dty = 2 + DateDiff("d", j1, DateSerial(y, 12, 31)) 'days this year
    If diff > dty Then
        result = 1
    End If
    If diff < 0 Then
        result = 0
    End If
    If diff > 0 And diff <= dty Then
        result = diff / dty
    End If
    percent_year_worked = result
End Function

Function prior_value(line As String) As Variant
' Get the prior years' value for this line. Suitable only for year columns.
    Dim prior_col As String
    Dim value As Variant
    Dim table As String
    Dim rng As Range
    Set rng = Application.caller
    table = rng.ListObject.Name
    prior_col = y_offset(this_col_name(), -1)
    value = get_val(line, table, prior_col)
    prior_value = value
End Function

Function ratio_to_start(account As String, category As String, y_year As String) As Double
'For investment income and expense, compute the ratio to the start balance, but use the prior end balance since
'that should have already been computed.  This allows the table to occur before the balances table in the compute order
'To be run in a cell in the invest_iande_work table.
    Dim work_table As String, bal_table As String
    Dim key As Variant
    Dim start_bal As Double, value As Double, ratio As Double
    work_table = Application.caller.ListObject.Name
    bal_table = "tbl_balances"
    On Error GoTo err1
    start_bal = get_val("End Bal" + account, bal_table, y_offset(y_year, -1), True)
    GoTo continue
err1:
    ' If we are on the first period, then the start value should be static and not require a calculation
    If 1729 = Err.Number - vbObjectError Then
        start_bal = get_val("Start Bal" + account, bal_table, y_year)
    Else
        log (Err.Description)
        ratio_to_start = 0
        Exit Function
    End If
continue:
    key = account + ":" + category + ":value"
    value = get_val(key, work_table, y_year)
    If start_bal = 0 Then
        ratio = 0
    Else
        ratio = value / start_bal
        ratio = Round(ratio, 4)
    End If
    ratio_to_start = ratio

End Function

Function retir_parm(code As String, who As String) As Variant
'Get a retirement paramenter given code and code (G or V)
    Dim rng As Range
    On Error GoTo ErrHandler
    sht = "retireparms"
    cl = InStr(1, "abGV", who, vbTextCompare)
    With ThisWorkbook.Worksheets(sht)
        Set rng = .Range("Table3[code]")
        rw = Application.WorksheetFunction.Match(code, rng, False)
        rw = rw + rng.Row - 1
        s = sht & "!" & .Cells(rw, cl).address
        v = .Range(s)
        retir_parm = v
    End With
    Exit Function

ErrHandler:
    log ("retir_parm: " & Err.Description & " (" & Err.Number & ")")
    log ("Looking for: " & code & " who:" & who)

End Function

Function RMD_1(account As String, account_owner As String, y_year As String, Optional death_year As Integer = 0) As Double
'return the req minimum distribution table 1 result for a year for a given account, owner (GBD or VEC) and year.
'if death year is not given then this function treat this as spousal inheritance
'if death year is given the treat this as a beneficiary inheritance
    Dim this_year As Integer, age As Integer
    Dim prior_end_bal As Double, life_expectancy As Double, result As Double
    this_year = IntYear(y_year)
    prior_end_bal = get_val("End Bal" & account, "tbl_balances", "Y" & this_year - 1)
    If death_year = 0 Then ' for spousal use actual age this year
        age = age_of(account_owner, y_year)
        life_expectancy = get_val(age, "tbl_rmd_1", "Life Expectancy")
    Else ' work with the age at year after death for beneficiary type
        age = age_of(account_owner, "Y" & (death_year + 1))
        life_expectancy = get_val(age, "tbl_rmd_1", "Life Expectancy")
        life_expectancy = life_expectancy - (this_year - (death_year + 1)) 'factor is reduced by one for each succeeding distribution year.
    End If
    result = prior_end_bal / life_expectancy
    RMD_1 = result
End Function

Function sort_tax_table()
'make sure the federal tax tables are sorted properly
    Dim tbl_name As String
    tbl_name = "tbl_fed_tax"
    ws = ws_for_table_name(tbl_name)
    Dim tbl As ListObject
    Set tbl = ThisWorkbook.Worksheets(ws).ListObjects(tbl_name)
    Dim year_column As Range, Range_column As Range
    Set year_column = Range(tbl_name & "[Year]")
    Set Range_column = Range(tbl_name & "[Range]")
    With tbl.sort
       .SortFields.Clear
       .SortFields.Add key:=year_column, SortOn:=xlSortOnValues, Order:=xlAscending
       .SortFields.Add key:=Range_column, SortOn:=xlSortOnValues, Order:=xlAscending
       .Header = xlYes
       .Apply
    End With
End Function

Sub test_fed_tax()
    Dim r As Double, c As Double
    
    zt = "not passed"
    r = Federal_Tax(2150, 9999)
    If 0 = r Then zt = "passed"
    n = 74031
    pt = "not passed"
    r = Federal_Tax(2020, 350000)
    If r = n Then pt = "passed"
    n = 72331
    ct = "not passed"
    c = Fed_Tax_CapGn(2020, 350000, 10000)
    If c = n Then ct = "passed"
    Debug.Print ("Zero test: " & zt)
    Debug.Print ("Positive test:" & pt)
    Debug.Print ("Capital gains test:" & ct)
  
End Sub

Sub test_get_val()
    Dim tbl_name As String
    Dim line_name As String
    Dim y_year As String
    Debug.Print (get_val("Expenses:T:Soc Sec - TOTAL", "tbl_iande_actl", "Y2018"))
    Debug.Print (get_val("End BalReal Estate", "tbl_balances", "Y2019"))

 End Sub

Sub test_LUMP()
    Dim val As Double
    val = LUMP("401K - GBD - TRV", "Y2022")
    Debug.Print (val)
End Sub

Sub test_medicarePrem()
Dim test_cases() As Variant
Dim yr As String
Dim infl As Variant
Dim magi As Variant
test_cases() = Array(Array(2021, 1#, 10000), Array(2022, 1#, 182001), Array(2022, 1#, 400000), Array(2023, 1.02, 75000))
log ("Part B tests")
For i = LBound(test_cases) To UBound(test_cases)
    yr = "Y" & test_cases(i)(0)
    magi = test_cases(i)(2)
    infl = test_cases(i)(1)
    partB = PartBPrem(yr, infl, magi)
    partD = PartDSurcharge(yr, infl, magi)
    msg = "Input: year=" & test_cases(i)(0) & " magi=" & magi & " inflation=" & infl & "   Output: " & partB & "  Part D: " & partD
    log (msg)
Next


End Sub

Sub test_mo_apply()
Dim test_cases() As Variant
Dim test_case As Variant
Dim yr As String
Dim start_date As Date, end_date As String, result As Double
test_cases() = Array( _
Array(3, 2022, 2022), _
Array(12, 2025, 2025), _
Array(3, 2022, 2022, 11, 2022), _
Array(3, 2022, 2025, 9, 2025), _
Array(3, 2022, 2022, 8, 2022) _
)
log ("mo_apply tests")
For i = LBound(test_cases) To UBound(test_cases)
    test_case = test_cases(i)
    start_date = DateSerial(test_case(1), test_case(0), 1)

    yr = "Y" & test_case(2)
    end_date = "-none-"
    If UBound(test_case) > 2 Then
        end_date = test_case(3) & "/1/" & test_case(4)
        result = mo_apply(start_date, yr, end_date)
    Else
        result = mo_apply(start_date, yr)
    End If
    msg = "Input: year=" & yr & " start/end dates = " & start_date & " " & end_date & "   Output: " & result
    log (msg)
Next i
End Sub

Sub test_sort()
    sort_tax_table
End Sub

Function this_col_name() As String
'return the caller's column name, assuming the cell is in a table.
'Otherwise generates a #VALUE  error
'Use to make formulas more portable

    Dim point As Range
    Dim list_ojb As ListObject
    Dim cols As ListColumns
    Dim offset As Integer, col_ix As Integer
    
    Set point = Application.caller
    Set list_obj = point.ListObject
    Set cols = list_obj.ListColumns
    offset = list_obj.Range(1, 1).Column - 1
    col_ix = offset + point.Column
    this_col_name = cols(col_ix)
End Function

Function ws_for_table_name(tbl_name As String) As String
' find out what worksheet the named table occurs on
    With ThisWorkbook.Worksheets("utility")
        Set rng = .ListObjects("tbl_table_map").DataBodyRange
        ws = Application.WorksheetFunction.VLookup(tbl_name, rng, 2, False)
    End With
    ws_for_table_name = ws
End Function

Function y_offset(y_year As String, offset As Integer) As String
'given a y_year offset it by the amount given, producing a new y_year
    y = IntYear(y_year)
    r = "Y" & y + offset
    y_offset = r
End Function
```