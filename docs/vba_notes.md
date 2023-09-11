# VBA notes

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

# applescript bits

tell application "Microsoft Excel"
	activate
	set my_file to POSIX file "/Users/george/argus/budget/data/test_wb.xlsm"
	open my_file
end tell
set stamp to get the current date
set output to stamp & " - excel_save: Opened excel file."
log output
delay 10