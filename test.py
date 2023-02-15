#!/usr/bin/env python

# short demonstration of passing preliminary code to the repl
# instead of writing your own repl

import parser

STR="""
This is the example program
this is more 
38293829 3829 3892
"string"
"a string that
continues
to the next
line"
"""
parser.repl(code=STR);
