IoWiki do(
// STUFF YOU MUST CHANGE:

password := "abernathy" // This password should be overridden in LocalConfig.io even if nothing else is.

// STUFF YOU MAY WELL WANT TO CHANGE:

homeDirectory := (launchPath .. "/pages/") 
    // or "/var/www/IoWiki/", or whatever

// Email notification of changes:
	notifyFrom := "" // This is the address notifications will come from.  It should be the address of someone who can edit this file in case of complaints.
	notifyEmailAddresses := "" // add email addresses to this, separated by commas
	notifySubject := method( "IoWiki: recent changes" ) // alternatives include: notifySubject := method( "IoWiki: " .. self name )
	emailPrefix := "" // prefix for the body of the email
	minimumNotificationInterval := 24 // in hours

pictureSuffixes := List clone append (".jpg",".JPG",".png",".PNG",".gif",".GIF")

historyPageSizeLimit := 100 * 1024 
    // There's no limit to how much history IoWiki will record --- deliberately so, for security --- 
    // but we don't want displaying page history to take too long, so only this many characters are 
    // displayed.  If a user needs more page history than this, they'll have to ask the system 
    // administrator for it.

logFilePath := "log"



// SPAM BLOCKING
blockContents := ""
        // "", or a regular expression: pages which match this expression after editing won't be saved.


// STUFF WHICH IS OPERATING-SYSTEM-DEPENDENT:

IoWiki diffsCommand := method ("(echo \"\n----\"; echo " .. Date clone now asString .. "; echo \"\n\n\"; diff --ignore-case --ignore-space-change --unchanged-group-format='' --old-group-format='[[[break]]]deleted at line %df: *red {code %<}*' --new-group-format='[[[break]]]added at line %de: *lime {code %>}*' --changed-group-format='[[[break]]]changed line %df from: *orange {code %<}*[[[break]]]to: *green {code %>}*' \"" .. homeDirectory cloneAppendPath (self name) .. ",previous\" \"" .. homeDirectory cloneAppendPath (self name) .. "\" 2>/dev/null) | cat - \"" .. homeDirectory cloneAppendPath (self name) .. ",history\" | cat > \"" .. homeDirectory cloneAppendPath (self name) .. ",temp-history\"; mv \"" .. homeDirectory cloneAppendPath (self name) .. ",temp-history\"  \"" .. homeDirectory cloneAppendPath (self name) .. ",history\"")

// If you're running IoWiki on a system which can't run the GNU diff command, uncomment 
// the following line:
// Lobby diffsCommand := method ("")



// IGNORE STUFF BELOW THIS LINE UNLESS YOU'RE A BORN FIDDLER.



// Stuff to translate if running in languages other than English:
editButtonText := "Edit Page"
restoreButtonText := "Undo"
homeButtonText := "Home"
pageHistoryButtonText := "Page History"
instructionsButtonText := "Instructions"
homePageName := "HomePage"
passwordSectionText := "Password:"
instructionsPageName := "IoWikiInstructions"
recentChangesPageName := "RecentChanges"
pageTemplateName := "PageTemplate"
HTMLLineEnding := "\r\n" // CR LF
redirectionMarkup := "redirect://"
recentChangesFileName := "recent changes"
noPageYet := "This topic awaits." .. HTMLLineEnding .. "No-one has written it yet." .. HTMLLineEnding .. "You are its poet."
noDiffsYet := "This page has never been edited, so there is no history to report on."
Sequence editPrefix := method ("<form name='editing' action='" .. self lastPathComponent .. "' method='post'><textarea name='editedPage' rows='37' cols='50'>") // delete this later
Sequence editPrefix1 := method ("<form name='editing' action='" .. self lastPathComponent .. "' method='post'>")
editPrefix2 := "<textarea name='editedPage' rows='37' cols='50'>"
editPasswordPart := "password: <input name='password' type='text' value='' SIZE='10' MAXLENGTH='225'><br><br>"
editSuffix := "</textarea><br><input type='submit' name='action' accesskey='c' value='Cancel'><input type='submit' name='action' accesskey='s' value='Save'></form><br><br>"
pageTemplateBannedMessage := "This is a page template.  For security reasons, you can't edit it without permission from the site administrator."
pagePasswordBannedMessage := "This page is protected by a password."
recentChangesBannedMessage := "Sorry: you can't edit the recent changes page, because other people rely on the way it's generated automatically."
pageTemporarilyLockedMessage := "This page has temporarily been locked."
noPreviousPageToRestoreMessage := "Sorry: I have no previous version of that page to show you."


// Things you might want to change to change hotlinking behaviour:

URLPattern := "((http|https|mailto|ftp|news|gopher)://|mailto:)[^\\t\\n\\f\\r\\x20\\(\\),;\\[\\]]*([A-Za-z0-9:\\/])"
WikiWordContextPattern := "\\A(<.*>)*(\\W*)"
	// Stuff before the WikiWord, which may include HTML tags and white space.
WikiWordWithDotPattern := "([A-Za-z]*\\.[A-Za-z\\']+[A-Za-z0-9\\.\\-\\']*[A-Za-z0-9])"
	// (i)  At least one dot anywhere in the word except at the end, and at least three characters long.
WikiWordCamelCasePattern := "([A-Z]*[a-z0-9\\.\\-]+[A-Z][A-Za-z0-9\\'\\.\\-]*[A-Za-z0-9])"
	// (ii) One or more capital letters followed by at least one lower-case letter followed by a capital letter followed by at least one other character.


// Globals which I don't think anyone will need to change:
mapDelimiter := "[[[.]]]"
illicitCharacter := "/" // directory separator in linux and BSD; override with ":" on HFS-formatted volumes (MacOS)
projectSeparator := "-"
projectSeparatorFormattedForDisplay := " &mdash; "
pageTitleMarker := "<PAGE TITLE>"
pageMessageMarker := "<PAGE MESSAGE>"
pageNameMarker := "<PAGE NAME>"
pageTextMarker := "<PAGE TEXT>"
editButtonMarker := "<EDIT BUTTON>"
restoreButtonMarker := "<RESTORE PREVIOUS VERSION BUTTON>"
homeButtonMarker := "<HOME BUTTON>"
pageHistoryButtonMarker := "<PAGE HISTORY BUTTON>"
instructionsButtonMarker := "<INSTRUCTIONS BUTTON>"
passwordSectionMarker := "<PASSWORD SECTION>"
contentTypeHeader := "Content-type: text/html"
minimalPageTemplate := "<html><body><EDIT BUTTON><HOME BUTTON><PAGE HISTORY BUTTON><INSTRUCTIONS BUTTON><h1><PAGE NAME></h1><PAGE TEXT></body></html>"
)
