"""
A series of wrappers.
"""

import json
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


class JsonHandling:
    """
    This module contains the `JSON` class that allows to load and save `.json`
    files in a pre-defined format.
    """

    def __init__(self, filename):
        self.file = filename
        self.dic = {}

    def dic2json(self):
        """Save file in JSON format"""
        with open(self.file, 'w') as filename:
            json.dump(self.dic, filename, sort_keys = True, indent = 4,
                      separators=(',', ':'))

    def json2dic(self):
        """Load a JSON file into a dictionary"""
        self.dic =  json.load(open(self.file))
