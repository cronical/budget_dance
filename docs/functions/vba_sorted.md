# VBA Code
``` vbscript
Attribute VB_Name = "Module1"

Public Const dbg As Boolean = False
Option Base 0

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

Sub log(txt As String)
    fn = ThisWorkbook.Path & "/fcast_log.txt"
    Open ThisWorkbook.Path & "/log.txt" For Append As #1
    Print #1, (Format(Now, "mm/dd/yyyy HH:mm:ss: ") & txt)
    Close #1
End Sub

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
    start_bal = get_val(account + ":Start Bal", bal_table, y_offset(y_year, -1), True)
    GoTo continue
err1:
    ' If we are on the first period, then the start value should be static and not require a calculation
    If 1729 = Err.Number - vbObjectError Then
        start_bal = get_val(account + ":Start Bal", bal_table, y_year)
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

Sub test_get_val()
    Dim tbl_name As String
    Dim line_name As String
    Dim y_year As String
    Debug.Print (get_val("Expenses:T:Soc Sec - TOTAL", "tbl_iande_actl", "Y2018"))
    Debug.Print (get_val("End BalReal Estate", "tbl_balances", "Y2019"))

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
