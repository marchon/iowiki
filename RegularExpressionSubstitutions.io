// Regular expression substitutions, with wild cards.  Jason.Grossman@staff.usyd.edu.au, 2004-5

// usage example: "wombats are cuddly" rSubstitute ("([a-z][ao][a-z])([a-z][ao][a-z])", "\\2-\\1")
//       	  ==> "bat-woms are cuddly"

Lobby regexCache := Map clone
Sequence rSubstitute := method (findRegex, substituteRegex,
	r := regexCache atIfAbsentPut (findRegex, Regex clone setPattern (findRegex)) // cache compiled regular expressions, for speed
	r setString (self asString)
	regexMap := Map clone
	maxSubstitutionTerms := substituteRegex split ("\\") size // a fast way of getting an upper bound on the number of substitution terms
	r allMatches foreach (i, v,
		if (v type != "List") then (v := list (v))
		for (n, maxSubstitutionTerms, 0,
			groupN := v at (n)
			regexMap atPut ("\\" .. n asString, groupN or "")
		)
		self := self replaceSeq (v at (0), substituteRegex asBuffer replaceMap (regexMap))
	)
	self
)