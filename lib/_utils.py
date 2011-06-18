#!/usr/bin/env python

import subprocess

def subprocessPiped(pargs, stdin=""):
    """
    Executes subprocess with pargs with input stdin, and returns the 3-tuple

    (retcode, stdout, stderr)
    """
    proc = subprocess.Popen(pargs, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    s, e = proc.communicate(stdin)
    return (proc.returncode, s, e)
