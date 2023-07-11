use applescript version "2.4"
use scripting additions
tell application "Microsoft Excel"
  activate
  set my_file to POSIX file "/Users/george/argus/budget/data/test_wb.xlsm"
  open my_file
end tell  
set stamp to get the current date
set output to  stamp & " - excel_save: Opened excel file."
log output
tell application "Microsoft Excel"
  calculate full rebuild
end tell
set stamp to get the current date
set output to  stamp & " - excel_save: called for calculate full rebuild"
log output
delay 3
tell application "Microsoft Excel"
  save
  quit
end tell
set stamp to get the current date
set output to  stamp & " - excel_save: Saved excel file"
log output
