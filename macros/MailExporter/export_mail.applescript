-- Scurry: Mail Exporter Ñ Full Extraction with Attachments (v7)
-- Extracts selected email from Apple Mail: metadata, body, and attachments.

-- === CONFIGURATION ===
set stagingRoot to (POSIX path of (path to home folder)) & "Projects/scurry/tmp/"

tell application "Mail"
	-- Get the list of currently selected messages in the frontmost viewer
	set selectedMessages to selected messages of message viewer 1
	
	-- Guard: make sure something is actually selected
	if (count of selectedMessages) is 0 then
		display dialog "No message selected." buttons {"OK"} default button "OK"
		return
	end if
	
	-- Grab the first selected message
	set theMessage to item 1 of selectedMessages
	
	-- Extract metadata fields
	set theSubject to subject of theMessage
	set rawSender to sender of theMessage
	set theDate to date received of theMessage
	set theBody to content of theMessage
	
	-- Format the date as "YYMMDD vHHMM" for folder naming
	-- and "YYYY-MM-DD HH:MM" for the email.txt header
	set isoDate to (theDate as Çclass isotÈ as string)
	
	set folderDate to do shell script Â
		"date -j -f '%Y-%m-%dT%H:%M:%S' '" & isoDate & "' '+%y%m%d v%H%M'"
	
	set headerDate to do shell script Â
		"date -j -f '%Y-%m-%dT%H:%M:%S' '" & isoDate & "' '+%Y-%m-%d %H:%M'"
	
	-- Sanitize subject for use in folder names
	set sanitizedSubject to do shell script Â
		"echo " & quoted form of theSubject & Â
		" | sed 's/[:\\/\\\\*?\"<>|]//g' | sed 's/  */ /g' | sed 's/^ *//;s/ *$//'"
	
	-- Build the folder name and full path
	set folderName to folderDate & " " & sanitizedSubject
	set folderPath to stagingRoot & folderName & "/"
	
	-- Create the directory
	do shell script "mkdir -p " & quoted form of folderPath
	
	-- Normalize sender to bare email address
	if rawSender contains "<" then
		set AppleScript's text item delimiters to "<"
		set afterBracket to text item 2 of rawSender
		set AppleScript's text item delimiters to ">"
		set theSender to text item 1 of afterBracket
		set AppleScript's text item delimiters to ""
	else
		set theSender to rawSender
	end if
	
	-- Recipients: extract addresses from recipient objects
	set toList to {}
	repeat with r in to recipients of theMessage
		set end of toList to address of r
	end repeat
	
	set ccList to {}
	repeat with r in cc recipients of theMessage
		set end of ccList to address of r
	end repeat
	
	set bccList to {}
	repeat with r in bcc recipients of theMessage
		set end of bccList to address of r
	end repeat
	
	-- Convert lists to comma-separated strings
	set AppleScript's text item delimiters to ", "
	set toStr to toList as rich text
	set ccStr to ccList as rich text
	set bccStr to bccList as rich text
	set AppleScript's text item delimiters to ""
	
	-- Save attachments and build the attachment list for email.txt
	set attachmentLines to ""
	set attachmentList to mail attachments of theMessage
	
	repeat with att in attachmentList
		set attName to name of att
		-- Save the attachment file into the folder
		-- `save` requires an AppleScript file reference, not a POSIX string,
		-- so we convert with `POSIX file`
		save att in POSIX file (folderPath & attName)
		-- Build the "(attached: filename)" line
		set attachmentLines to attachmentLines & return & "(attached: " & attName & ")"
	end repeat
	
	-- Build email.txt content: headers + blank line + body + attachment list
	set emailContent to Â
		"From: " & theSender & return & Â
		"To: " & toStr & return & Â
		"Cc: " & ccStr & return & Â
		"Bcc: " & bccStr & return & Â
		"Subject: " & theSubject & return & Â
		"Datetime: " & headerDate & return & Â
		return & Â
		theBody
	
	-- Append attachment list if there are any
	if (count of attachmentList) > 0 then
		set emailContent to emailContent & return & attachmentLines
	end if
	
	-- Write email.txt
	set emailFilePath to folderPath & "email.txt"
	do shell script "cat > " & quoted form of emailFilePath & " <<'SCURRY_EOF'
" & emailContent & "
SCURRY_EOF"
	
	-- Confirmation with attachment count
	set attCount to count of attachmentList
	if attCount is 0 then
		set attInfo to "no attachments"
	else if attCount is 1 then
		set attInfo to "1 attachment"
	else
		set attInfo to (attCount as rich text) & " attachments"
	end if
	
	display dialog "Saved to: " & folderName & return & "(" & attInfo & Â
		")" buttons {"OK"} default button "OK"
end tell
