# VBA notes

All VBA has been stripped out.  This page simply captures some of the bits that seemed worth preserving.

## Attempt to complete calculation

### clsAppEvents

Option Explicit

Private WithEvents mApp As Application
Private Sub Class_Initialize()
    Set mApp = Application
End Sub

Private Sub mApp_AfterCalculate()
    log ("Calc ended at: " & Now)
    ConsumeAfterCalculate
End Sub

### on open in ThisWorkbook

Private mAppEvents As clsAppEvents


Private Sub Workbook_Open()
    log ("workbook opened")
    mEnableConsume = True
    Set mAppEvents = New clsAppEvents
    log "Calc started " & Now
    Application.Calculate 'recalculates all formulas
 End Sub

#### Stripped



Private Sub Workbook_Open()
    log ("workbook opened")
    log "Calc started " & Now
    Application.Calculate 'recalculates all formulas
 End Sub

 ### consume in Module1

Public mEnableConsume As Boolean

Public Sub ConsumeAfterCalculate()
    If mEnableConsume Then
        ActiveWorkbook.Save
        log ("Saved " & Now)
        mEnableConsume = False
    End If
End Sub

# this_column_name

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

# log

Sub log(txt As String)
    fn = ThisWorkbook.Path & "/fcast_log.txt"
    Open ThisWorkbook.Path & "/log.txt" For Append As #1
    Print #1, (Format(Now, "mm/dd/yyyy HH:mm:ss: ") & txt)
    Close #1
End Sub


# applescript bits

tell application "Microsoft Excel"
	activate
	set my_file to POSIX file "/Users/george/argus/budget/data/test_wb.xlsx"
	open my_file
end tell
set stamp to get the current date
set output to stamp & " - excel_save: Opened excel file."
log output
delay 10

# debug 

    {
      "name": "oledump args",
      "type": "python",
      "request": "launch",
      "program": "util/oledump.py",
      "console": "integratedTerminal",
      "args": ["-r","-v","--vbadecompress", "./tmp/vbaProject/VBA/Module1"],
      "justMyCode": true
    },
    {
      "name": "sort_vba args",
      "type": "python",
      "request": "launch",
      "program": "dance/util/vba/sort_vba.py",
      "console": "integratedTerminal",
      "args": ["-i","vba/fcast.vb","-o","vba/fcast_sorted.vb","-x","docs/functions/vba_index.md","-s","docs/functions/vba_sorted.md"],
      "justMyCode": true
    },