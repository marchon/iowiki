# "Configurability is the root of all evil" -- Axel Liljencrantz,  http://fishshell.org/user_doc/design.html (1 May 2008)
#

# Modify the lines below to your taste.  Uncomment any lines you modify, by removing the initial comment sign (//).
IoWiki do(

// STUFF YOU MUST CHANGE:

password := "whatever"
	// Set this to something unique to your site, unless you don't mind wiley hackers being able to 
	// execute arbitrary HTML on your server (which is something you SHOULD mind).

// STUFF YOU MAY WELL WANT TO CHANGE:

// historyPageSizeLimit := 100 * 1024 
    // There's no limit to how much history IoWiki will record --- deliberately so, for security --- 
    // but we don't want displaying page history to take too long, so only this many characters are 
    // displayed.  If a user needs more page history than this, they'll have to ask the system 
    // administrator for it.


// SPAM BLOCKING
blockContents := ""
	// "", or a regular expression: pages which match this expression after editing won't be saved.

)
