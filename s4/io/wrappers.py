"""
Wrapper to some other softwares, like IDL and GDL.
"""

import subprocess as sp

def run_command(cmd, do_log = False):
    """
    Run a command on the shell.

    Parameters
    ----------

    cmd: str;
        A command line

    do_log: bool, opt;
        If True, wirte stdout and stderr to a file.

    Returns
    -------

    stdout: str;
        The output of the command

    stderr: str;
        the error output of the command
    """

    subp = sp.Popen(cmd, stderr = sp.PIPE, stdout = sp.PIPE, shell = True)

    (stdout, stderr) = subp.communicate()

    if do_log:
        with open('run.log', 'w') as out:
            out.write('{}\n{}'.format(stdout, stderr))
    else:
        return stdout, stderr
