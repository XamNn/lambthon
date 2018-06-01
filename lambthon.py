import re

letre = re.compile(r"^(\w+)=([^=].*)")
whitespacere = re.compile("\s+")
lambdare = re.compile(r"\^(\w+)\.")
escapedidenre = re.compile(r"\$(\w+)")
idenre = re.compile(r"(?<![\$\w])(\w+)")

idenprefix = "lmb_"

decls = []
names = {}

def getwithstring(s):
    for i, e in enumerate(decls):
        if e[0] == s:
            return (i, e)
    return (-1, None)
def getwithfunc(f):
    for i, e in enumerate(decls):
        if e[1] == f:
            return (i, e)
    return (-1, None)
def getnames(i):
    for name, index in names.items():
        if index == i:
            yield name
    return

def tidystr(val):
    return whitespacere.sub(" ", val.strip()).\
    replace("^ ", "^").\
    replace(" .", ".").\
    replace(". ", ".").\
    replace(" =", "=").\
    replace("= ", "=")

def makestr(val):
    for match in reversed(list(idenre.finditer(val))):
        val = val[:match.start()] + idenprefix + match.group(1)
    for match in reversed(list(escapedidenre.finditer(val))):
        val = val[:match.start()] + match.group(1)
    for match in reversed(list(lambdare.finditer(val))):
        val = val[:match.start()] + "lambda\t" + match.group(1) + ":(" + val[match.end():] + ")"
    val = "(" + val
    i = 0
    while i < len(val):
        if val[i] == " ":
            i += 1
            val = val[:i-1] + ")(" + val[i:]
        else:
            i += 1
    return val.replace("\t", " ") + ")"

def process(text):
    if (text == "exit"):
        raise SystemExit
    if (text.startswith("load ")):
        file = text[5:]
        if "." not in file:
            file += ".lambthon"
        with open(file) as f:
            for line in f:
                process(line)
        return
    if text.startswith("!! "):
        exec(text[3:])
        return
    if len(text) == 0:
        return
    text = tidystr(text)
    #print(text)
    letmatch = letre.match(text)
    try:
        if letmatch:
            name = idenprefix + letmatch.group(1)
            try:
                del names[name]
            except: pass
            valstr = letmatch.group(2)
            val = eval(makestr(valstr))
            if callable(val):
                (declindex, decl) = getwithstring(valstr)
                if decl == None:
                    (declindex, decl) = getwithfunc(val)
                else:
                    val = decl[1]
                if decl == None:
                    declindex = len(decls)
                    decls.append((valstr,val))
                else:
                    val = decl[1]
                names[name] = declindex
            globals()[name]=val
        else:
            val = eval(makestr(text))
            valstr = ""
            if callable(val):
                (declindex, decl) = getwithfunc(val)
                if decl == None:
                    (declindex, decl) = getwithstring(text)
                if decl != None:
                    valstr = decl[0]
                    for name in getnames(declindex):
                        valstr += " = " + name

            if (valstr == ""):
                valstr = str(val)
            print(valstr)

    except SyntaxError:
        print("Syntax Error")
    except NameError as e:
        print(str(e).replace("' ", "\" ").replace("'" + idenprefix, "\"").replace("'", "\"$"))
    except BaseException as e:
        print(e)

while True:
    process(input("lambthon> ").strip())
