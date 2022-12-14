use applescript version "2.4"
use scripting additions
tell application "Microsoft Excel"
  activate
  set my_file to POSIX file "/Users/george/argus/budget/data/test_wb.xlsm"
  open my_file
  save
  quit
end tell
