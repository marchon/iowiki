#!/usr/local/bin/ioServer


IoWiki := Object clone do( version := "IoWikiCGI version 0.1.04" )

/*

This software and the software distributed with it are copyright (2008) Jason Grossman.

Permission is granted to use all or part of this software for any purpose, subject to the
following restrictions:

1. This software is distributed without any warranty; without even the implied warranty of
merchantability or fitness for a particular purpose.

2. Altered versions of this software must be plainly marked as such, and must not be represented 
as being IoWiki.  Rationale: it would be a hassle if there were programs with different feature 
sets floating around under the same name.  You are free to release your own version of this software 
under a different name.

Jason

*/

// TEMPORARY:
Lobby true := Object clone do( type := "true"; clone := method( Nil ); setSlot := method( Nil ))
Object nil := Nil


WikiPage := Object clone
/* Read configuration files, which override each other in this order:
Defaults.io in this directory(the same directory as this script); then /etc/config.io; then config.io in this directory.
These files set slots in IoWiki, an object which stores server globals such as the port number.
These are per-server defaults.  (At the moment, IoWiki only allows one server, but that could change.)
These default values are imported from the file Defaults.io. */
doFile( launchPath cloneAppendPath( "Defaults.io" ))
try( doFile( cloneAppendPath( "/etc/IoWiki.cfg" ))) 
	/* But don't worry if that's not there. */
( doFile( launchPath cloneAppendPath( "LocalConfig.io" ))) 
	/* But, again, don't worry if that's not there either.  All we really need is Defaults.io. */
Lobby appendProto( IoWiki )
doFile( launchPath cloneAppendPath( "RegularExpressionSubstitutions.io" ))

// Read in the list of locked pages:
lockedPages := File clone setPath( launchPath cloneAppendPath( "LockedPages.txt" )) openForReading readLines

/*************************************************************************************************

	PAGE FORMATTING METHODS

**************************************************************************************************/

Sequence formatForHeading := method( 
	result := self asMutable do(
	    // Pretty-print the title by putting a little space between words:
		rSubstitute( "[A-Z]", " \\0" )
    	rSubstitute( "([A-Za-z])([0-9])", "\\1 \\2" )
		replaceSeq( projectSeparator, projectSeparatorFormattedForDisplay )
		replaceSeq( ",history", " &mdash page history" )))

linkedImagePattern := "{<img src='\\0' alt='automatically linked image from \\0 .'></img>}"

WikiPage linkPictureURL := method( word,
	pictureSuffixes foreach( i, v,
		if( word asString endsWithSeq( v ),
			word rSubstitute( URLPattern, linkedImagePattern )
			return word ))
	Nil )

linkedNormalURLPattern := "{<a href='\\0'>\\0</a>}"

WikiPage linkNormalURL := method( word,
	word rSubstitute( URLPattern, linkedNormalURLPattern ))

//    linkedWikiWordPattern := """{\\1\\2<a href="../\\3">\\3</a>}"""
    linkedWikiWordPattern := "{\\1\\2<a href=\"../\\3\">\\3</a>}" // silly hack because this doesn't seem to work with """ the way it should

Sequence obfuscateEmailAdddress := method( self replaceSeq("@", "&#64;"))

WikiPage linkWikiWord := method( word,
	if( word containsSeq( "@" ), return (word obfuscateEmailAdddress))
		// because it's almost certainly an email address, so it shouldn't be a candidate for being a WikiWord.
	if( word containsSeq( ".." ), return word replaceSeq( "..", "" ))
		// because ".." is the markup for disabling WikiWords.
//	if( word containsSeq( projectSeparator )) then(
//		word rSubstitute( WikiWordContextPattern .. WikiWordWithProjectSeparatorPattern, linkedWikiWordPattern )) else(
			if( word clone removeSuffix( "." ) containsSeq( "." )) then(
				word rSubstitute( WikiWordContextPattern .. WikiWordWithDotPattern, linkedWikiWordPattern )) else(
					word rSubstitute( WikiWordContextPattern .. WikiWordCamelCasePattern, linkedWikiWordPattern )))

IoWiki literalMap := Map clone
IoWiki nextIndex := 0

IoWiki uniqueIndex := method( IoWiki nextIndex := IoWiki nextIndex + 1 ) 
	/* As it happens this counts up from 0, but all that matters is that it returns a 
	unique identifier. */
	
Sequence parseLiterals := method( 
	while( true,
		nextLiteralStart := self findSeq( "{" ) or break
		nextLiteralStop := 0;
		try( nextLiteralStop := self findSeq( "}", nextLiteralStart ) + 1 )
			/* This will fail if there is no } to match the { we've found. */
		if( nextLiteralStop == 0, break )
		nextLiteral := self slice( nextLiteralStart, nextLiteralStop )
		nextLiteralTag := "[[[" ..( uniqueIndex ) asString .. "]]]"
		self replaceSeq( nextLiteral, nextLiteralTag )
		nextLiteral := nextLiteral slice( 1, -1 ) 
			/* to get rid of the { } */
		IoWiki literalMap atPut( nextLiteralTag, nextLiteral )))

WikiPage formatDetails := method( page,
	p := HTMLLineEnding .. page .. HTMLLineEnding 
		/* to prevent the regular expressions below from having to have exceptions for 
		the top and bottom of the page */
	p := p asMutable
	p replaceSeq( "<", "&lt;" ) replaceSeq( ">", "&gt;" ) 
		/* so that text that's preserved as literal by { } delimiters can't be interpreted as HTML, 
		which would be a security hole */
	p replaceSeq("...", "{...}")
		/* so that ellipses don't get mangled, since we're going to count "." as a metacharacter. */
		
	/* Now pull out text delimited by { }, and words prefixed by .., to be preserved as literals 
	and put back in at the last moment. */
	p parseLiterals 
		/* pulls out text delimited by { } */
	literalMap foreach( i, v, 
		if( v slice( 0, 4 ) == "pre ", literalMap atPut( i,"<pre>" .. v removeSlice( 0, 4 ) .. "</pre>" )))
	literalMap foreach( i, v, 
		if( v slice( 0, 5 ) ==( "pre" .. HTMLLineEnding ), literalMap atPut( i, "<pre>" .. v removeSlice( 0, 5 ) .. "</pre>" )))
	literalMap foreach( i, v, 
		if( v slice( 0, 4 ) == "code", literalMap atPut( i,"<code>" .. v removeSlice( 0, 4 ) replaceSeq( "\n", "<br>" ) .. "</code>" )))
			/* Code is saved with <code> HTML markup, but with line endings made significant. */
	p rSubstitute( "([^\\.] )\\.\\.([^\\.\\$].+?)([^\\w\\-\\.\\$_!/] )", "\\1{\\2}\\3" ) 
		/* This changes the .. prefix to { } delimiters. */
	p parseLiterals 
		/* This pulls out text delimited by { } again.  This time, it's text which was prefixed 
		by .. until a moment ago. */
		
	p replaceSeq( HTMLLineEnding, " <br>" )
	p replaceSeq( "[[[break]]]", " <br>" ) 
		/* [[[break]]] is used in the patterns in Defaults.io to code a break that can't be 
		interfered with by page contents. */
	p rSubstitute( "(<br>\\s* ){2,}", "<br><br>" ) 
		/* to reduce multiple <br>s to a maximum of two in a row ... among other advantages, this 
		makes the behaviour of various browsers more consistent with each other. 
		Possibly the \\s in this line ought to be something like( \\s|\\n|\\r|\\v|\\f ), but \\s 
		is faster and seems to work. */
	p replaceSeq( "[[[version]]]", IoWiki version )
	
	/* Make links to WikiWords and URLs. */
	words := p asString split(" ", "\t", HTMLLineEnding )
	p empty
	words foreach( j, word,
		word := word asMutable
		if( word findSeq( ":" ),
			self linkPictureURL( word ) or self linkNormalURL( word )
			,
			self linkWikiWord( word ))
		p appendSeq( " " ) appendSeq( word ))
	
	p parseLiterals
		/* pulls out text delimited by { } again ... this time, it's the links we've just made 
		(which we've enclosed in { }) */

	p replaceSeq( "----", "<br><hr>" )
	p replaceSeq( "---", "&mdash;" )
	p replaceSeq( "--", "&ndash;" )
	p replaceSeq( "``", "&ldquo;" )
	p replaceSeq( "''", "&rdquo;" )
	p replaceSeq( "[[[(]]]", "{" ); p replaceSeq( "[[[)]]]", "}" ) 
		/* for documenting the { } markup */

	p rSubstitute( "<br>-&gt;(.+?)<br>", "<br><ul>\\1</ul><br>" )
	p rSubstitute( "<br>&ndash;&gt;(.+?)<br>", "<br><ul><ul>\\1</ul></ul><br>" )
	p rSubstitute( "<br>&mdash;&gt;(.+?)<br>", "<br><ul><ul><ul>\\1</ul></ul></ul><br>" )
	p rSubstitute( "<br>\\* (.+?)<br>", "<br><ul><li>\\1</li></ul><br>" )
	p rSubstitute( "<br>\\*\\* (.+?)<br>", "<br><ul><ul><li>\\1</li></ul></ul><br>" )
	p rSubstitute( "<br>\\*\\*\\* (.+?)<br>", "<br><ul><ul><ul><li>\\1</li></ul></ul></ul><br>" )
	p rSubstitute( "<br>-(.+?)<br>", "<br><ul><li>\\1</li></ul><br>" )
	p rSubstitute( "<br>&ndash;(.+?)<br>", "<br><ul><ul><li>\\1</li></ul></ul><br>" )
	p rSubstitute( "<br>&mdash;(.+?)<br>", "<br><ul><ul><ul><li>\\1</li></ul></ul></ul><br>" )
	p replaceSeq( "</ul><br>", "</ul>" )
//	p rSubstitute( "<br>###(.+?)(<br>)+?", "<br><h2>\\1</h2>" )
	p rSubstitute( "<br>##(.+?)(<br>)+?", "<br><h2>\\1</h1>" )
	p rSubstitute( "<br>#(.+?)(<br>)+?", "<br><h3>\\1</h3>" )
	p rSubstitute( "\\*red(.+?)\\*", "<font color='#a00000'><span id='red'>\\1</span></font>" )
	p rSubstitute( "\\*crimson(.+?)\\*", "<font color='#a00000'><span id='crimson'>\\1</span></font>" )
//      crimson is just a synonym for red, kept for backwards compatibility of some pages on xeny.net
	p rSubstitute( "\\*blue(.+?)\\*", "<font color='#0000a0'><span id='blue'>\\1</span></font>" )
	p rSubstitute( "\\*green(.+?)\\*", "<font color='#009000'><span id='green'>\\1</span></font>" )
	p rSubstitute( "\\*lime(.+?)\\*", "<font color='#00f000'><span id='lime'>\\1</span></font>" )
	p rSubstitute( "\\*purple(.+?)\\*", "<font color='#a000f0'><span id='purple'>\\1</span></font>" )
	p rSubstitute( "\\*fawn(.+?)\\*", "<font color='#a0a040'><span id='fawn'>\\1</span></font>" )
	p rSubstitute( "\\*pink(.+?)\\*", "<font color='#ff1080'><span id='pink'>\\1</span></font>" )
	p rSubstitute( "\\*orange(.+?)\\*", "<font color='#ff9000'><span id='orange'>\\1</span></font>" )
	p rSubstitute( "\\*black(.+?)\\*", "<font color='#000000'><span id='black'>\\1</span></font>" )
	p rSubstitute( "\\*code(.+?)\\*", "<span id='code'><code>\\1</code></span>" )
	p rSubstitute( "\\*(.+?)\\*", "<strong>\\1</strong>" )
	p rSubstitute( "_(.+?)_", "<em>\\1</em>" )
	
	/* Replace the literals( the segments of the page that were removed earlier to preserve them 
	from being interpreted by the markup code ): */
	p := p replaceMap( IoWiki literalMap ) asMutable
	
	/* Final tidying-up of line endings: */
	p rSubstitute( "(<br>\\s* ){2,}", "<br><br>" )
	p rSubstitute( "</ul>\\s*<br>\\s*<hr>", "</ul><hr>" ) 
		/* because </ul> adds a lot of vertical space */
	p rSubstitute( "(<br>\\s* )+<hr>\\s*<br>\\s*<br>", "<br><br><hr><br>" ) 
		/* to tidy up vertical space around horizontal rules */
	p replaceSeq( "<br>", "<br>" .. HTMLLineEnding ); p replaceSeq( "<li>", HTMLLineEnding .. "<li>" ) 
		/* to make the page source more human-readable */
	p clipBeforeEndOfSeq( "<br>" ) 
		/* to get rid of the spare one we added at the beginning */
	p )

WikiPage formatContent := method( 
	if( self rawContent == Nil, return )
	if( self rawContent beginsWithSeq( "@@@" ),
		self formattedContent := "<pre>" .. self rawContent asMutable removeSlice( 0, 2 ) replaceSeq( "<", "&lt;" ) .. "</pre>"
		,
		self formattedContent := formatDetails( self rawContent ))
	
	IoWiki pageToFormat := self
		// Now pageToFormat is accessible within the following do clause.  self isn't :-( .  Not happy with this hack.  Should refactor.
	self formattedContent := self findPageTemplate asMutable do( 
		replaceSeq( pageTextMarker, pageToFormat formattedContent ) 
		replaceSeq( pageTitleMarker, pageToFormat name ) 
		replaceSeq( pageNameMarker, pageToFormat name formatForHeading ) 
		replaceSeq( passwordSectionMarker, passwordSectionText )
		replaceSeq( editButtonMarker, "<span id='edit'><a href='" asMutable .. pageToFormat name lastPathComponent .. "?action=edit' accesskey='e'>" .. editButtonText .. "</a></span>" )
		replaceSeq( homeButtonMarker, "<span id='home'><a href='" asMutable ..  homePageName .. "'  accesskey='h'>" .. homeButtonText .. "</a></span>" ) 
		replaceSeq( pageHistoryButtonMarker, "<span id='diff'><a href='" asMutable ..  pageToFormat name .. "?action=diff'  accesskey='p'>" .. pageHistoryButtonText .. "</a></span>" ) 
		replaceSeq( instructionsButtonMarker, "<span id='instructions'><a href='" asMutable ..  instructionsPageName .. "'  accesskey='i'>" .. instructionsButtonText .. "</a></span>" ))
	pageToFormat formattedContent )


/********************************************************************************************************

	MAIN METHODS

*********************************************************************************************************/

Cache := Map clone
// List linePrint := method(l, l foreach(i, v, writeln(i, ": ", v ))) // for debugging

// Start logging if required.  Note that in Io, the log method need only be defined if logging is required; otherwise it needn't even 
// exist.  How's that for elegance and efficiency?
IoWiki nonNilString := method(s, if(s, s, ""))
IoWiki logString := method( s, "IoWiki " .. s .. " on port " .. port .. if( self ?host, " for IP address " .. self host, "" ) .. " at " .. Date now asString )

// IoWiki log := method( s, @@writeln( logString( nonNilString(s) )))
// or
// IoWiki logFile := File clone setPath( launchPath cloneAppendPath( logFilePath ))
// IoWiki log := method( s, 
//	logFile openForAppending write ( logString( nonNilString(s) ) .. "\n") close
// )
// or just comment out both options if you don't want logging at all

// next line temporarily commented out while server is constantly restarting due to Io bug
//?log( "IoWiki server starting at " .. serverAddress )

if( ?blockContents and( ?blockContents != "" ),
	spamRegularExpressionFinder := Regex clone setPattern( blockContents )
	IoWiki isSpam := method( spamRegularExpressionFinder setString( self ) hasMatch ))

Sequence removeFromCache := method( pageName,
	Cache foreach(i, v, if( try( i beginsWithSeq( self )), Cache removeAt( i ))))

Sequence camelCase := method( 
	Sequence join( projectSeparator join( self split( projectSeparator ) mapInPlace( part, part asCapitalized )) split( "." ) mapInPlace( part, part asCapitalized )))

IoWiki templateCache := Map clone
IoWiki siteTemplateFile := File clone setPath( homeDirectory cloneAppendPath( pageTemplateName ))

Sequence loadTemplate := method( requestedTemplate,
	// ?log( "loading template " ..( if( self != "", self, "(default)" )))
	// When loading page templates, first try the explicitly requested page template, if any; then try projectName/pageTemplateName; 
	// then try pageTemplateName; then give up and use the built-in template.
	requestedTemplateFile := File clone setPath( homeDirectory cloneAppendPath( requestedTemplate .. projectSeparator .. pageTemplateName ))
	projectTemplateFile := File clone setPath( homeDirectory cloneAppendPath( self .. projectSeparator .. pageTemplateName ))
	if( requestedTemplateFile exists,
		return requestedTemplateFile asString,
		if( projectTemplateFile exists,
			return projectTemplateFile asString
			,
			return if( siteTemplateFile exists, siteTemplateFile asString, minimalPageTemplate ))))

WikiPage findPageTemplate := method( 
	projectName := ""
	projectSeparatorPosition := self name reverseFindSeq(projectSeparator)
	if( projectSeparatorPosition,
	   projectName :=  self name slice( 0, projectSeparatorPosition))
	if( self ?requestedTemplate,
		return projectName loadTemplate( self requestedTemplate )
		,
		return templateCache atIfAbsentPut( projectName, projectName loadTemplate( "" ))))

WikiPage pageLoad := method( 
	self rawContent := self file exists ?asString or IoWiki noPageYet )

WikiPage pagePrepare := method( 
	self file := File clone setPath( homeDirectory cloneAppendPath( self name ))
	self pageLoad
	if( self name endsWithSeq( ",history" ),
		if( self rawContent == noPageYet,
			self rawContent := noDiffsYet
			,
			self rawContent := self rawContent slice( 0, historyPageSizeLimit )))
	self formatContent
	if( self name endsWithSeq( ",history" ),
		self formattedContent replaceSeq( "<head>", """<head><META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW">""")
		self formattedContent replaceSeq( "<HEAD>", """<head><META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW">"""))
	self )
	
IoWiki sendRedirectionHeaders := method(redirectionAddress,
	self request sendResponse( 301, "Moved Permanently" )
	self request sendHeader( "Location", redirectionAddress )
	WikiPage ?log("redirecting " .. page name .. " to " .. redirectionAddress)
	request endHeaders
	request close)
	
IoWiki sendNormalHeaders := method(
	request sendResponse( 200, "OK" )
	request sendHeader( "Content-type", "text/HTML" )
	request sendHeader( "Expires", "Tue, 01 Jan 2002 00:00:00 GMT" )
    request sendHeader( "Cache-Control", "no-store, no-cache, must-revalidate" )
    request endHeaders)	

// Initialise recent changes lists:
recentChangesFile := File clone setPath(homeDirectory .. recentChangesFileName )
recentChangesRSSFile := File clone setPath(homeDirectory .. "rss" )

Map store := method( f,
		f remove
		f openForUpdating
		// try( f truncateToSize(0 )) // currently not working - Io bug?
	self foreach(i, v,
		f write( i, mapDelimiter, v, mapDelimiter )
		f flush ))

Map load := method( f,
	l := f openForUpdating asString split( mapDelimiter )
	while( l size > 0,
		value := l pop
		key := l pop
		self atPut(key, value )
	self ))

recentChanges := Map clone
IoWiki recentChangesRSS := Map clone
recentChanges load( recentChangesFile )
IoWiki recentChangesRSS load( recentChangesRSSFile )
recentChangesPage := WikiPage clone do( 
	name := recentChangesPageName )

if( ?recentChangesPageLimit > 0,
	resizeRecentChanges := method(
		while( recentChanges count > recentChangesPageLimit,
			recentChanges removeAt(recentChanges keys pop )
			IoWiki recentChangesRSS removeAt(IoWiki recentChangesRSS keys pop )
			)))
			
WikiPage escapeIfPageLocked := method(
// When the user tries to edit a locked page, we give an error message (see the Edit method).
// When the user tries to view a locked page, we show it to them in the normal way.
// When the user tries to do anything else with a locked page (see diffs, save it, ...) we 
// exit with prejudice.
// This is important, because it's our main anti-spam measure.
    if( lockedPages contains (self name), System exit )
)

WikiPage updateRecentChanges := method(
    try( self escapeIfPageLocked )
	try(
		// This try will fail the first time around, when we're just initialising the recent changes lists.  That's fine.
		recentChanges removeAt( self ?name )
            // Remove earlier references to this page, so the Map will stay sorted by date.
		recentChangesLine := ""
		nameLinked := linkWikiWord(self name clone)
		if(nameLinked == self name,
            // then the page name isn't recognisable as a wiki word, so we'd better add a dot to force it to be linked later
            recentChangesLine := "."
		)
		recentChangesLine := recentChangesLine .. self name .. Date now asString( " (%d %B %Y, %H:%M %Z)\n" )
		IoWiki recentChangesRSSLine := "<item><title>" .. self name .. "</title><link>" .. "http://xeny.net/" .. self name .. "</link><description><![CDATA[" .. Date now asString( " %d %B %Y, %H:%M %Z\n" ) .. "]]></description></item>"
		recentChanges atPut( self name, recentChangesLine )
		IoWiki recentChangesRSS atPut( self name, IoWiki recentChangesRSSLine )
		)
		
	?resizeRecentChanges
	recentChangesPage rawContent :=( HTMLLineEnding join( recentChanges values ))
	recentChangesPage formatContent
	Cache atPut( recentChangesPageName .. "+", recentChangesPage )
	recentChanges store( recentChangesFile )
	IoWiki recentChangesRSS store( recentChangesRSSFile ))
WikiPage updateRecentChanges // to initialise the recent changes page

WikiPage saveDiffs := method(
    try( self escapeIfPageLocked )
	previousFileName := homeDirectory cloneAppendPath( self name ) .. ",previous"
	File clone setPath( previousFileName ) open 
		// to create the file if it doesn't already exist
	try( System system( self diffsCommand )))
		// See Defaults.io for the definition of WikiPage diffsCommand.  It's there because it contains strings that people 
		// might want to translate into other languages.

if( notifyEmailAddresses and(
	notifyEmailAddresses != ""),
	WikiPage notify := method(
		mail := Sequence clone append( "From: " .. notifyFrom .. "\n" )
		mail append( "To: " .. notifyEmailAddresses .. "\n" )
		mail append( "Subject: " ) append( notifySubject ) append( "\n\n" )
		try( mail append( ?emailPrefix ))
		try( mail append( Cache at( recentChangesPageName .. "+" ) rawContent ))
		writeln( mail append( Cache at( recentChangesPageName .. "+" ) rawContent )) // debug
		mail append( "\n.\n" ) // mail-end token
		mail replaceSeq( "'", "&quot;" )
		if( System system( "echo '" .. mail .. "' | sendmail -t " ) == 0, IoWiki lastNotification := Date clone now )
		System system( "sendmail -q" ) // deliver the mail queue
		?log( "notifying " .. notifyEmailAddresses ))
	,
	WikiPage notify := Nil )

IoWiki lastNotification := Date clone now

WikiPage lessUrgentUpdateTasks := method( 
	// Save the changes back to the file system, fairly safely:
	// self file path pathComponent linePrint // debug
	Directory clone setPath( self file path pathComponent ) create 
	tempFile := File clone setPath( self file path .. ".temp" )
	tempFile openForUpdating write( self rawContent ) close
	try( self file moveTo( self file path .. ",previous" ))
	tempFile moveTo( self file path )
	self saveDiffs
	self updateRecentChanges
//	if(	?lastNotification secondsToNow > minimumNotificationInterval * 60 * 60 ,
//		self @@notify )
)

WikiPage update := method( 
	try( self escapeIfPageLocked )
	    if( (self password != IoWiki password) and (self name != "ThomasForster"),
	        errorMessage := pagePasswordBannedMessage
    		self formatForEditing( errorMessage ) print
    		System exit )
	    
	if( self name endsWithSeq( pageTemplateName ),
		Cache empty
		templateCache empty
		lessUrgentUpdateTasks
		self formatContent
		,
		self formatContent
		self name removeFromCache
		Cache atPut( self name .. "+" ..( self requestedTemplate or "" ), self )
//		self @@lessUrgentUpdateTasks )
		self lessUrgentUpdateTasks )
	?log( "saving  " .. self name ))
		
WikiPage postEditTasks := method(
    try( self escapeIfPageLocked )
	if( self editedVersion != self rawContent,
		if( self editedVersion ?isSpam,
			?log( "received spam:" .. "\n" .. self editedVersion .. "\n ..." )
			,
			self rawContent := self editedVersion
			update )))

WikiPage formatForEditing := method( s,
	self findPageTemplate asMutable replaceSeq( pageNameMarker, self name formatForHeading ) replaceSeq( pageTitleMarker, self name ) replaceSeq( pageTextMarker, s ))

WikiPage edit := method( 
	withoutSuffix := self name asMutable removeSuffix( ",history" )
	if( withoutSuffix != self name, 
		// then self is a history page
		self name := withoutSuffix
		self pagePrepare edit
		// I think that line should be( Cache atIfAbsentPut( withoutSuffix "+" ..( self requestedTemplate or "" ), self pagePrepare ) edit ), 
		// but for some reason that doesn't work.  I don't know why not.
		return )
    errorMessage := Nil
	if( self name == "RecentChanges", errorMessage := recentChangesBannedMessage )
	if( self name endsWithSeq( pageTemplateName ),
		if( self password != IoWiki password, errorMessage := pageTemplateBannedMessage ))
	if( lockedPages contains (self name), errorMessage := pageTemporarilyLockedMessage )
	if( errorMessage isNil,
	    if( self name == "ThomasForster",
	        self formatForEditing( self name editPrefix .. self rawContent .. self name editSuffix ) print,
            self formatForEditing( self name editPrefix1 .. self name editPasswordPart .. self name editPrefix2 .. self rawContent .. self name editSuffix ) print),
		self formatForEditing( errorMessage ) print )
	?log( "editing " .. self name ))
	
WikiPage rss := method(
	"""<?xml version="1.0" encoding="utf-8"?><rss version="2.0">
	 <channel>
	 <title>xeny.net recent changes</title>
	 <link>http://xeny.net/recent.changes</link>
	 <description><![CDATA[xeny.net recent changes]]></description>""" print
	
	HTMLLineEnding print
	HTMLLineEnding print
	
	(HTMLLineEnding join( IoWiki recentChangesRSS values )) print
	
	HTMLLineEnding .. "</channel></rss>" print
	
	// ?log("serving RSS")
	)

WikiPage diff := method(
    try( self escapeIfPageLocked )
	page := WikiPage clone
	page name := self name asMutable removeSuffix( ",history" ) .. ",history"
	page pagePrepare
//	"Page history is not working at the moment.  I'll have it fixed soon.  Jason" print )
	page formattedContent print )

WikiPage restore := method(
    try( self escapeIfPageLocked )
	previousFile := self file clone setPath( homeDirectory cloneAppendPath( self name asMutable removeSuffix( ",previous" ) .. ",previous" ))
	if( previousFile exists,
		currentFile := self file
		self file := previousFile
		self pageLoad
		self file := currentFile
		self formatContent
		self show
		self update
		,
		self formatForEditing( noPreviousPageToRestoreMessage ) print ))

WikiPage show := method( 
	if( self rawContent == noPageYet, self edit, self formattedContent print )
	?log( "serving " .. self name ))

WikiPage Cancel := method( if( self file exists, self show, self name := homePageName; self pagePrepare; self show ))

WikiPage Save := method(try( self escapeIfPageLocked ); self postEditTasks; self show )

/************************************************************************************************************

	MAIN PROGRAM

*************************************************************************************************************/


// Make our server run at the IP address which was set in Defaults.io or config.io.
// HttpServer setAddress(serverAddress)

// Install a handler in the http server:
// HttpServer serve( port, HttpRequest,
    IoWiki page := WikiPage clone
// page host := HttpRequest mySocket host
	
	query := CGI clone parse
    // here we ought to do something special to cope with the program crashing on the parse 
    // if there's nothing to parse ... if that's even possible

// query := HttpRequest queryArgs
// query foreach(i, v, page ?log( v ) ) // debug
	
	// Load the requested page contents and format the page
	// (converting slashes to semicolons, which means that semicolons are more or less 
	// reserved characters in page names -- you can use them, but ambiguity may result):
    page name := query at ("imageMapX") asMutable replaceSeq(illicitCharacter, ";") camelCase
    // the name "imageMapX", for the first nameless parameter, is a default set by the Io CGI library
	if( page name == "FaviconIco", return )
	   // bugger Favicons
	if( page name == "", page name := homePageName )
	page requestedTemplate := query at( "template" )
	
	// Get the page from the cache, or format the page and put it into the cache. ( I love the semantics of atIfAbsentPut. )  
	// Either way, proceed using a clone of the copy in the cache so that if page changes while it's being formatted the cache doesn't change.  
	// page shouldn't change while it's being formatted, so the cloning is redundant.  It's there to avoid future bugs.
	page := Cache atIfAbsentPut( page name .. "+" ..( page ?requestedTemplate or "" ), page pagePrepare ) clone 

	page editedVersion :=( query at( "editedPage" ) or "" ) 
		// If we've just come from an edit page, query at( "editedPage" ) is what was in the textarea.
	page password := ( query at( "password" ))
			
// Tell the send method to send its output to this server:
// IoWiki request := HttpRequest
// IoWiki send := method( request send( self ))
		
	
// If the very first thing on the page is "redirect://" then we instruct the client browser to redirect to another web page ...
// unless the client is trying to edit the page.  If we're not redirecting then we send encouraging headers.  We can do this 
// straight away, since there's no such thing as a nonexistent wiki page.
//	if((page rawContent beginsWithSeq(redirectionMarkup) and (query at("action") != "edit")),
//		sendRedirectionHeaders(page rawContent asMutable clipBeforeEndOfSeq(redirectionMarkup))
//	,	
//		sendNormalHeaders)
// NOTE TO SELF: DO REDIRECTIONS IN THE WEB SERVER FROM NOW ON
	
	action := query at( "action" ) or "show"
	// ?log(action)
	if( action type != "Sequence", action := "show" )
	if( WikiPage hasSlot( action ), nil, action := "show" )
	page perform( action asMessage )
	
