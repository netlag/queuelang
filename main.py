#!/usr/bin/env python

import importlib
import sys
import os

import parser

def main(*args, **kwargs):

    modname = None
    #try:
    #    modname = os.environ["testing_mod"]
    #except Exception:
    #    modname = "QL.parser"

    parser = importlib.import_module(modname if modname else "parser")
    #print(parser)

    times = 1
    while True:

        try:
            parser.repl(sys.argv)

        except:
            print(sys.exc_info())

        try:
            input("Hit enter to reload parser> ")
        except KeyboardInterrupt:
            print("Interrupted")
            break
        except EOFError:
            print("EOF")
            break

        newparser = importlib.reload(parser)
        parser = newparser
        #print(parser)

########## MAIN ##################

if (__name__ == "__main__"):
    #parser.repl()
    # tries to reload parser between repls
    main(sys.argv)
    ...
