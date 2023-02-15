#!/usr/bin/env python

## FILE: parser.py
# An interpreter of a language
# I think it's a context-free grammar

import sys
import time
from enum import Enum


class State(Enum):
    NONE = 0
    TEXT = 1
    TEND = 2
    SYMBOL = 3
    SSPACE = 4
    NUMBER = 5
    NDEC = 6
    NFRAC = 7
    NEXP = 8
    NSIGN = 9

    # might be fun to handle repeating decimals??
    # or we can just do these as fractions
    def chr(self):
        return [
            "NONE", "TEXT", "TEND", "SYMBOL", "SSPACE", "NUMBER", "NDEC",
            "NFRAC", "NEXP", "NSIGN"
        ][self.value]


class TokenType(Enum):
    NONE = 0
    ERROR = ord('E')
    OPER = ord('X')
    TEXT = ord('T')
    SYMBOL = ord('S')
    NUMBER = ord('N')
    QUEUE = ord('Q')

    def chr(self):
        return chr(self.value)


def symbolstart(char, state):
    return state == State.NONE and (
        char.isidentifier() or char in "'_"
    )


def symbolcont(char, state):
    return state == State.SYMBOL and (
        char.isidentifier() or char.isdecimal()
                                      or char in "'_"
    )

def symbolscont(char, state):
    return state == State.SSPACE and (
        char.isidentifier() or char.isdecimal()
        or char in "'_"
    )

def symbolspace(char, state):
    return state == State.SYMBOL and char.isspace()

def symbolskip(char, state):
    return state == State.SSPACE and char.isspace()

def signstart(char, state):
    return state in [State.NONE, State.NSIGN] and char in "+-"


def numberstart(char, state):
    return state in [State.NONE, State.NSIGN] and char.isdecimal()


def numbercont(char, state):
    return state == State.NUMBER and char.isdecimal()


def decstart(char, state):
    return state in [State.NONE, State.NUMBER, State.NDEC, State.NFRAC, State.NEXP] and char in ".,"


def deccont(char, state):
    return state == State.NDEC and char.isdecimal()


def fracstart(char, state):
    return state in [State.NUMBER, State.NDEC, State.NFRAC, State.NEXP] and char in "/"


def fraccont(char, state):
    return state == State.NFRAC and char.isdecimal()


def expstart(char, state):
    return state in [State.NUMBER, State.NDEC, State.NFRAC, State.NEXP] and char in "eE"


def expcont(char, state):
    return state == State.NEXP and char.isdecimal()


def textstart(char, state):
    return state == State.NONE and char in "\""


def textcont(char, state):
    return state == State.TEXT and char not in "\""


def textend(char, state):
    return state == State.TEXT and char in "\""


class Context:
    token = ""
    queue = []
    symtab = {}
    state = State.NONE


# determines the token type
# evaluate if the token is complete
def processtoken(context):
    if context.state == State.TEXT:
        # partial text
        return

    if not len(context.token) > 0:
        print("Ignoring empty token")
        return

    tokentype = TokenType.NONE
    if (context.state == State.SYMBOL or context.state == State.SSPACE):
        tokentype = TokenType.SYMBOL
    elif context.state == State.TEND:
        tokentype = TokenType.TEXT
    elif context.state in [
            State.NUMBER, State.NDEC, State.NFRAC, State.NEXP, State.NSIGN
    ]:
        tokentype = TokenType.NUMBER
    else:
        tokentype = TokenType.OPER

    #print("Processing Token: ", tokentype.chr(), context.token)

    evaltoken(context.token, tokentype, context)
    cleartoken(context)


def cleartoken(context):
    #print("Token cleared: ", context.token)
    context.token = ""
    context.state = State.NONE


# add token to queue, or process operator
def evaltoken(token, tokentype, context):
    queue = context.queue
    #print("Eval: ", tokentype.chr(), token)

    if tokentype != TokenType.OPER:
        # evaluates to itself
        queue.append((tokentype, token))
        #print("Appended New Token: ", context.token)
    elif token == "@":
        context.queue = (TokenType.QUEUE, queue)
    elif token == "*" and len(queue) > 0 and queue[-1][0] == TokenType.QUEUE:
        v = queue.pop()
        queue.extend(v[1])
        #print("Exploded: ", v)
    elif token == "*" and len(queue) > 0 and queue[-1][0] == TokenType.SYMBOL:
        symbol = queue[-1][1]
        try:
            symval = context.symtab[symbol.lower()]
        except KeyError:
            print("Symbol undefined: ", symbol)
            symval = (TokenType.ERROR, '')
        queue[-1] = symval
    elif token == "=" and len(queue) > 1 and queue[-1][0] == TokenType.SYMBOL:
        symbol = queue[-1][1]
        context.symtab[symbol.lower()] = queue[-2]
        v = queue.pop()
        v2 = queue.pop()
        print("Assigned: ", v[1], v2)
    elif token == "~" and len(queue) > 0:
        v = queue.pop()
        print("Deleted: ", v[0].chr(), v[1].encode())
    else:
        # mark leftovers an error
        queue.append((tokentype, token))
        print("Meaningless token: ", token)
    #endif

###################################
# process input code, can be multiline
import copy


def parse(context=Context(), code=""):
    oldcontext = context
    context = copy.deepcopy(oldcontext)
    # ok to start in a string but not a symbol/number
    assert (context.state in (State.NONE, State.TEXT))

    #if len(context.token) > 0:
    #    print("Processing legacy token: ", context.token)
    #    processtoken(context)

    # TODO: Fix error with parsing "123abc"
    for char in code:
        if textend(char, context.state):
            #print("TEXTEND")
            context.token += char
            context.state = State.TEND
            processtoken(context)
            continue
        elif textcont(char, context.state):
            #print("TEXTCONT")
            context.token += char
            continue
        elif symbolcont(char, context.state):
            #print("SYMBOLCONT")
            context.token += char
            continue
        elif symbolscont(char, context.state):
            #print("SYMBOLSCONT")
            context.state = State.SYMBOL
            context.token += " "
            context.token += char
            continue
        elif symbolspace(char, context.state):
            context.state = State.SSPACE
            #print("SYMBOLSPACE")
            #context.token += " "  # replace char
            continue
        elif symbolskip(char, context.state):
            # discard extra whitespace in symbol
            #print("SYMBOLSPACESKIP")
            #context.token += char
            continue
        elif numbercont(char, context.state):
            #print("NUMBERCONT")
            context.state = State.NUMBER
            context.token += char
            continue
        elif deccont(char, context.state):
            #print("DECCONT")
            context.token += char
            continue
        elif fraccont(char, context.state):
            #print("FRACCONT")
            context.token += char
            continue
        elif expcont(char, context.state):
            #print("EXPCONT")
            context.token += char
            continue
        elif numberstart(char, context.state):
            #print("NUMBERSTART")
            context.state = State.NUMBER
            context.token += char
            continue
        elif symbolstart(char, context.state):
            #print("SYMBOLSTART")
            context.state = State.SYMBOL
            context.token += char
            continue
        elif signstart(char, context.state):
            #print("SIGNSTART")
            context.state = State.NSIGN
            context.token += char
            continue
        elif decstart(char, context.state):
            #print("DECSTART")
            context.state = State.NDEC
            context.token += char
            continue
        elif fracstart(char, context.state):
            #print("FRACSTART")
            context.state = State.NFRAC
            context.token += char
            continue
        elif expstart(char, context.state):
            #print("EXPSTART")
            context.state = State.NEXP
            context.token += char
            continue
        elif textstart(char, context.state):
            #print("TEXTSTART")
            context.state = State.TEXT
            context.token += char
            continue

            
        # token can't continue
        # process whatever we already have
        if len(context.token) > 0:
            processtoken(context)

        # skip spaces
        if char.isspace():
            #print("SPACE")
            continue

        # all other chars are singleton
        #print("OPER")
        context.token += char
        context.state = State.NONE
        processtoken(context)
    #endfor
    pass

    # anything left?
    if context.state == State.TEXT:
        context.token += '\n'
    elif len(context.token) > 0:
        processtoken(context)

    # end of line reached
    return context


################################
def printcontext(context):
    if not context:
        #print("Current Context: ", context)
        return
    #print("Current Context:")
    #print("State: ", context.state.chr())
    if len(context.token) > 0:
        print("Token: ", context.tokentype.chr(), context.token.encode())
    if context.state == State.TEXT:
        print("Partial Text: ", context.token.encode())

    printqueue(context.queue)


def printqueue(queue=[], depth=0):
    if not queue:
        print(queue)
        return
    for qtup in queue:
        if qtup[0] == TokenType.QUEUE:
            for i in range(depth):
                print(" ", end="")
            print("[")
            printqueue(qtup[1], depth + 1)
            for i in range(depth):
                print(" ", end="")
            print("]")
        else:
            for i in range(depth):
                print(" ", end="")
            print(" ", qtup[0].chr(), qtup[1].encode())


###############################
def repl(*args, **kwargs):

    prompt = "*> "
    textprompt = "+> \""
    context = Context()
    code = None

    while True:
        # if we had been in a token, end it
        #if len(context.token) > 0 and context.state == State.NONE:
        #    processtoken(context)

        # reprinting the queue is too noisy while entering multiline text
        if not context.state == State.TEXT:
            printcontext(context)

        try:
            code = input(
                prompt if not context.state == State.TEXT else textprompt)
        except EOFError:
            print("EOF")
            break  # exit repl
        except KeyboardInterrupt:
            print("Interrupt")
            # discard partial tokens
            cleartoken(context)
            continue
            #try:
        #    newcontext = parse(context=context, code=code)
        #except:
        #    print("Parse Error: ", sys.exc_info())

        newcontext = parse(context=context, code=code)
        if not newcontext:
            print("Failed to rebuild context")
            print("Code lost: ", code)
            continue

        code = None
        # TODO: is this a fundamental logic error because parse is changing context
        assert (context != newcontext)
        context = newcontext

    #end repl loop
    if context.state == State.TEXT:
        context.token += "\""
        context.state = State.TEND
        print("Forced text termination")

    if len(context.token) > 0:
        processtoken(context)

    print("Final Context:")
    printcontext(context)
    #input("Hit Enter to Reload...")


########## MAIN ##################

if (__name__ == "__main__"):
    repl(sys.argv)
else:
    print("parser loaded", time.time())
