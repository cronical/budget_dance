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
```
