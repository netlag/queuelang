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

    times = 0
    while True:
        times += 1
        print(parser)

        try:
            parser.repl(sys.argv, times=times)

        except:
            print(sys.exc_info())

        try:
            input("Hit enter to reload parser, or ^D> ")
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
    main(sys.argv)
    ...
