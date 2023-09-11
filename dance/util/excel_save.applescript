use AppleScript version "2.4"
use scripting additions


tell application "Microsoft Excel"
	quit saving yes
end tell
set stamp to get the current date
set output to stamp & " - excel_save: Saved excel file"
log output
