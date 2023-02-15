#!/usr/bin/env python

## FILE: parser.py
# An interpreter of a language

import sys
import time

class Context:
    token = ""
    tokentype = "?"
    queue = []
    insymbol = False
    innumber = False
    intext = False

    pass
    
def processtoken(context):
        if context.intext:
            context.intext = False
            context.tokentype = "T"
        elif context.insymbol:
            context.insymbol = False
            context.tokentype = "S"
        elif context.innumber:
            context.innumber = False
            context.tokentype = "N"
        else:
            # must be an operator?
            context.tokentype = "X"

        evaltoken(context)

def cleartoken(context):
    context.tokentype = "?"
    context.token = ""
    context.intext = False
    context.insymbol = False
    context.innumber = False

    return

def evaltoken(context):
        print("Eval: ", context.tokentype, context.token)
        if context.tokentype != "X":
            # evaluates to itself
            context.queue.append((context.tokentype, context.token))
        elif context.token == "@":
            context.queue = [("Q", context.queue)]
        elif context.token == "*" and len(context.queue) > 0 and context.queue[-1][0] == "Q":
            v = context.queue.pop()
            context.queue.extend(v[1])
            print("Exploded: ", v)
        elif context.token == "*" and len(context.queue) == 2 and context.queue[-1][0] == "S":
            print("Symbol dereference not implemented")
        elif context.token == "~" and len(context.queue) > 0:
            v = context.queue.pop()
            print("Deleted: ", v)
            return
        else:
            # mark leftovers an error
            # context.append(('E', context.token))
            print("Meaningless token discarded: ", context.token)
        #endif
        cleartoken(context)

###################################
def parse(context=Context(), code=''):

    for char in code:
        # check for valid continuation
        if context.intext:
            context.token += char
            if char in "\"":
                processtoken(context)
            continue
        elif context.insymbol and (char.isidentifier() or char.isdecimal() or char in "_'"):
            context.token += char
            continue
        elif context.innumber and char.isdecimal():
            context.token += char
            continue

        # token not continuing
        if len(context.token) > 0:
            processtoken(context)

        # skip spaces
        if char.isspace():
            continue

        # are we starting a new long token or text string
        if char.isidentifier() or char in "'":
            context.insymbol = True
            context.token += char
            continue
        elif char.isdecimal() or char in "+-":
            context.innumber = True
            context.token += char
            continue
        elif char in "\"":
            context.intext = True
            context.token += char
            continue

        # skip spaces
        if char.isspace():
            continue

            # all other chars are singleton
        context.token += char
        processtoken(context)
    #endfor

    if len(context.token) > 0:
        if context.intext:
            context.token += "\n"
        else:
            processtoken(context)
    pass

    # end of input line reached
    return context


################################
def printcontext(context):
    if not context:
        #print("Current Context: ", context)
        return
    #print("Current Context:")
    if len(context.token) > 0:
        print("Token Type: ", context.tokentype)
        print("Token: ", context.token)
    if context.intext:
        print("Partial Text: ", context.token.encode())

    printqueue(context.queue)
    return

def printqueue(queue=[], depth=0):
    if not queue:
        print(queue)
        return
    for qtup in queue:
        if qtup[0] == 'Q':
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
            print(" ", qtup)

    return


###############################
def repl(*args, **kwargs):

    prompt = "*> "
    textprompt = "*> \""
    context = Context()

    while True:
        if not context.intext:
            printcontext(context)
        try:
            code = input(prompt if not context.intext else textprompt)
        except EOFError:
            print('EOF')
            cleartoken(context)
            break
            #cleartoken(context)
        except KeyboardInterrupt:
            print('Interrupted, Continuing...')
            print("Use control-D or 'x' to exit...")
            cleartoken(context)
            # skip parsing
            continue
        #try:
        #    newcontext = parse(context=context, code=code)
        #except:
        #    print("Parse Error: ", sys.exc_info())
        
        newcontext = parse(context=context, code=code)
        if not newcontext:
            print("Failed to rebuild context")
            continue

        context = newcontext

    #end repl loop
    if len(context.token) > 0:
        if context.intext:
            print("Text terminated")
            context.token += "\""
        processtoken(context)

    input("Hit Enter to Reload...")


########## MAIN ##################
if (__name__ == "__main__"):
    repl(sys.argv)
else:
    print("parser loaded", time.time())
