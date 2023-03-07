#!/usr/bin/env python

## FILE: parser.py
# An interpreter of a language
# I think it's a context-free grammar

import sys
import time
from enum import Enum

# this is to distinguish from debug
def telluser(*args, **kwargs):
    print(args, kwargs);

def debug(*args, **kwargs):
    print(args, kwargs);

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
    #return state == State.SYMBOL and char.isspace()
    # currently preventing entry to SSPACE state
    return state == State.SSPACE and char.isspace()

def symbolskip(char, state):
    return state == State.SSPACE and char.isspace()

def signstart(char, state):
    return state in [State.NONE, State.NSIGN] and char in "+-"


def numberstart(char, state):
    return state in [State.NONE, State.NSIGN] and char.isdecimal()


def numtosym(char, state):
    return state == State.NUMBER and char.isidentifier() or char in "'_"

def numbercont(char, state):
    return state == State.NUMBER and char.isdecimal() or char in "_"


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
    queue = list()
    symtab = {}
    state = State.NONE


# determines the token type
# evaluate if the token is complete
def processtoken(context):
    if context.state == State.TEXT:
        # partial text
        return

    if not len(context.token) > 0:
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

    evaltoken(context.token, tokentype, context)
    cleartoken(context)


def cleartoken(context):
    context.token = ""
    context.state = State.NONE


# add token to queue, or process operator
def evaltoken(token, tokentype, context):

    if tokentype != TokenType.OPER:
        context.queue.append((tokentype, token))
    elif token == "@":
        oldqueue = context.queue
        context.queue = list()
        context.queue.append((TokenType.QUEUE, oldqueue))
        telluser(context.queue, context)
    elif token == "*" and len(context.queue) > 0 and context.queue[-1][0] == TokenType.QUEUE:
        v = context.queue.pop()
        context.queue.extend(v[1])
    elif token == "*" and len(context.queue) > 0 and context.queue[-1][0] == TokenType.SYMBOL:
        symbol = context.queue[-1][1]
        try:
            symval = context.symtab[symbol.lower()]
        except KeyError:
            telluser("Symbol undefined: ", symbol)
            symval = (TokenType.ERROR, '')
        context.queue[-1] = symval
    elif token == "=" and len(context.queue) > 1 and context.queue[-1][0] == TokenType.SYMBOL:
        symbol = context.queue[-1][1]
        context.symtab[symbol.lower()] = context.queue[-2]
        v = context.queue.pop()
        v2 = context.queue.pop()
        telluser("Assigned: ", v[1], v2)
    elif token == "~" and len(context.queue) > 0:
        # TODO: probably should throw an error if nothing to delete
        v = context.queue.pop()
        telluser("Deleted: ", v[0].chr(), v[1].encode())
    else:
        # mark leftovers an error
        context.queue.append((tokentype, token))
        telluser("Meaningless token: ", token)
    #endif

###################################
# process input code, can be multiline
import copy


def parse(context=Context(), code=""):
    oldcontext = context
    context = copy.deepcopy(oldcontext)
    # ok to start in a string but not a symbol/number
    assert (context.state in (State.NONE, State.TEXT))

    # TODO: Fix error with parsing "123abc"
    for char in code:
        if textend(char, context.state):
            #debug("TEXTEND")
            context.token += char
            context.state = State.TEND
            processtoken(context)
            continue
        elif textcont(char, context.state):
            #debug("TEXTCONT")
            context.token += char
            continue
        elif symbolcont(char, context.state):
            #debug("SYMBOLCONT")
            context.token += char
            continue
        elif symbolscont(char, context.state):
            #debug("SYMBOLSCONT")
            context.state = State.SYMBOL
            context.token += " "
            context.token += char
            continue
        elif symbolspace(char, context.state):
            context.state = State.SSPACE
            #debug("SYMBOLSPACE")
            #context.token += " "  # replace char
            continue
        elif symbolskip(char, context.state):
            # discard extra whitespace in symbol
            #debug("SYMBOLSPACESKIP")
            #context.token += char
            continue
        elif numtosym(char, context.state):
            #debug("NUMTOSYM")
            context.state = State.SYMBOL
            context.token += char
            continue
        elif numbercont(char, context.state):
            #debug("NUMBERCONT")
            context.state = State.NUMBER
            context.token += char
            continue
        elif deccont(char, context.state):
            #debug("DECCONT")
            context.token += char
            continue
        elif fraccont(char, context.state):
            #debug("FRACCONT")
            context.token += char
            continue
        elif expcont(char, context.state):
            #debug("EXPCONT")
            context.token += char
            continue
        elif numberstart(char, context.state):
            #debug("NUMBERSTART")
            context.state = State.NUMBER
            context.token += char
            continue
        elif symbolstart(char, context.state):
            #debug("SYMBOLSTART")
            context.state = State.SYMBOL
            context.token += char
            continue
        elif signstart(char, context.state):
            #debug("SIGNSTART")
            context.state = State.NSIGN
            context.token += char
            continue
        elif decstart(char, context.state):
            #debug("DECSTART")
            context.state = State.NDEC
            context.token += char
            continue
        elif fracstart(char, context.state):
            #debug("FRACSTART")
            context.state = State.NFRAC
            context.token += char
            continue
        elif expstart(char, context.state):
            #debug("EXPSTART")
            context.state = State.NEXP
            context.token += char
            continue
        elif textstart(char, context.state):
            #debug("TEXTSTART")
            context.state = State.TEXT
            context.token += char
            continue

            
        # token can't continue
        # process whatever we already have
        if len(context.token) > 0:
            processtoken(context)

        # skip spaces
        if char.isspace():
            #debug("SPACE")
            continue

        # all other chars are singleton
        #debug("OPER")
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
def tellcontext(context):
    if not context:
        return
    if len(context.token) > 0:
        telluser("Token: ", context.tokentype.chr(), context.token.encode())
    if context.state == State.TEXT:
        telluser("Partial Text: ", context.token.encode())

    tellqueue(context.queue)


def tellqueue(queue=list(), depth=0):
    if not queue:
        #telluser(queue)
        return
    for qtup in queue:
        if qtup[0] == TokenType.QUEUE:
            for i in range(depth):
                telluser(" ", end="")
            telluser("[")
            tellqueue(qtup[1], depth + 1)
            for i in range(depth):
                telluser(" ", end="")
            telluser("]")
        else:
            for i in range(depth):
                telluser(" ", end="")
            telluser(" ", qtup[0].chr(), qtup[1].encode())


###############################
def repl(*args, **kwargs):

    times = (kwargs["times"] if "times" in kwargs else "*")
    prompt = str(times) + "> "
    textprompt = "+> \""
    context = Context()
    code = (kwargs["code"] if "code" in kwargs else None)

    while True:

        # reprinting the queue is too noisy while entering multiline text
        if not context.state == State.TEXT:
            tellcontext(context)

        try:
            if not code:
                code = input(prompt if not context.state == State.TEXT else textprompt)
        except EOFError:
            telluser("EOF")
            break  # exit repl
        except KeyboardInterrupt:
            telluser("Interrupt")
            # discard partial tokens
            cleartoken(context)
            continue

        newcontext = parse(context=context, code=code)
        if not newcontext:
            telluser("Failed to rebuild context")
            telluser("Code lost: ", code)
            continue

        code = None
        # TODO: is this a fundamental logic error because parse is changing context
        assert (context != newcontext)
        context = newcontext

    #end repl loop
    if context.state == State.TEXT:
        context.token += "\""
        context.state = State.TEND
        telluser("Forced text termination")

    if len(context.token) > 0:
        processtoken(context)

    telluser("Final Context:")
    tellcontext(context)

########## MAIN ##################

if (__name__ == "__main__"):
    repl(sys.argv)
else:
    #debug("parser loaded", time.time())
    ...
