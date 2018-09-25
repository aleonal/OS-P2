#!/usr/bin/env python3
import os, sys, time, re


def main():
    os.environ['PS1'] = "$: "

    while True:
        os.write(1, os.getenv('PS1').encode())
        parent()
        print()


def parent():
    args = input().split(" ")
    process1, process2 = parseArgs(args)

    if not process1 and not process2:
        return
    elif not process2:
        metaChild(process1)
    else:
        metaPipe(process1, process2)


def metaPipe(process1, process2):
    pr, pw = os.pipe()
    for f in (pr, pw):
        os.set_inheritable(f, True)

    import fileinput

    rc = os.fork()

    if rc < 0:
        os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
        og = os.dup(1)
        os.close(1)
        os.dup2(pw, 1)
        for fd in (pr, pw):
            os.close(fd)

        processExec(process1)
        os.dup2(og, 1)
    else:
        og = os.dup(0)
        os.close(0)
        os.dup2(pr, 0)
        for fd in (pw, pr):
            os.close(fd)

        metaChild(process2)
        os.dup2(og, 0)

    os.wait()


def metaChild(args):
    rc = os.fork()

    if rc < 0:
        os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
        processExec(args)
    else:
        childCode = os.wait()


def processExec(args):
    newArgs = changeIO(args)
    if '/' in args[0]:
        os.execve(args[0], newArgs, os.environ)

    for dir in re.split(":", os.environ['PATH']): # try each directory in path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, newArgs, os.environ) # try to exec program
        except FileNotFoundError:             # ...expected
            pass                              # ...fail quietly
    os.write(2, ("Command not found.\n").encode())
    sys.exit(-1)


def changeIO(args):
    newArgs = []
    iterator = 0
    control = 1
    for var in args:
        if any(var in args[iterator] for var in '<'):
            os.close(0)
            sys.stdin = open(args[iterator + 1], 'r')
            fd = sys.stdin.fileno()
            os.set_inheritable(fd, True)
            control = 0
        elif any(var in args[iterator] for var in '>'):
            os.close(1)
            sys.stdout = open(args[iterator + 1], 'w')
            fd = sys.stdout.fileno()
            os.set_inheritable(fd, True)
            control = 0

        if control > 0:
            newArgs.append(args[iterator])

        iterator += 1
    return newArgs


def parseArgs(args):
    args1 = []
    args2 = []

    # Checks whether user typed exit or if input is empty
    if "exit" in args[0] and len(args) == 1:
        sys.exit(0)
    elif not args:
        return args1, args2

    # Checks for I/O redirection or piping
    iterator = 0
    for var in args:
        if any(var in args[iterator] for var in '|'):
            # Separates first process' arguments from argument line
            subiterator = 0
            while subiterator < iterator:
                args1.append(args[subiterator])
                subiterator += 1

            # Separates second process' arguments from argument line
            while subiterator + 1 < len(args):
                args2.append(args[subiterator + 1])
                subiterator += 1

            return args1, args2
        iterator += 1

    return args, args2


if __name__ == '__main__':
    main()
else:
    main()
