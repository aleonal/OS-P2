import os, sys, time, re

def main():
    header()
    while True:
        metaFork()

def header():
    os.write(1, ("====================================\n\tWelcome to TxShell!\n------------------------------------\n").encode())
    os.write(1, ("\t Built-in Commands\n\n").encode())
    os.write(1, ('1. "exit" to exit\n').encode())
    os.write(1, ('2. ">" to redirect output | e.g. wc shell.py > output.txt\n').encode())
    os.write(1, ('3. "<" to redirect input | e.g. python3 iCountWords.py < wordlist.txt > output.txt\n').encode())
    os.write(1, ("====================================\n\n").encode())


def metaFork():
    pid = os.getpid()





    os.write(1, ("$ ").encode())
    args = input().split(" ")
    if "exit" in args[0] and len(args) == 1:
        sys.exit(0)
    elif not args[0]:
        return


    rc = os.fork()


    if rc < 0:
        os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
        metaChild(args)
    else:
        childCode = os.wait()

def metaChild(args):
    newArgs = redirects(args)

    for dir in re.split(":", os.environ['PATH']): # try each directory in path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, newArgs, os.environ) # try to exec program
        except FileNotFoundError:             # ...expected
            pass                              # ...fail quietly
    os.write(2, ("Command not found.\n").encode())
    sys.exit(-1)

def redirects(args):
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

if __name__ == '__main__':
    main()
