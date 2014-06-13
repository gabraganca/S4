"""
This class facilitate the input/output of abundance values to SYNPLOT.

Parameter
---------

abundance: str, dic;
    The chemical abundance of the elements. It can have two forms:
    * A dictionary with the key as the chemical element symbol of its
      atomic number and the value is the abundance for that element.
      E.g., `{2:10.93, 'N':7.83}` for He and N abundances.
    * String of abundances in the SYNPLOT format, i.e.,
      '[2, 2, 10.93, 7, 7, 7.83]'.

Methods
-------

to_synplot:
    Transform the abundances in a dictionary format to SYNPLOT format.

from_synplot:
    Transform the abundances from the SYMPLOT format to a dictionary.

    Parameter
    ---------

    elem: int, str;
        Chemical element. Can be its symbol or its atomic number.

"""
import os
import json
import re
import numpy as np


# Loads the chemical elements and their atomic numbers
PERIODIC = json.load(open(os.path.dirname(__file__)+\
                          '/chemical_elements.json'))


class Synplot_abund():
    """
    This class facilitate the input/output of abundance values to SYNPLOT.

    Parameter
    ---------

    abundance: str, dic;
        The chemical abundance of the elements. It can have two forms:
        * A dictionary with the key as the chemical element symbol of its
          atomic number and the value is the abundance for that element.
          E.g., `{2:10.93, 'N':7.83}` for He and N abundances.
        * String of abundances in the SYNPLOT format, i.e.,
          '[2, 2, 10.93, 7, 7, 7.83]'.

    Methods
    -------

    to_synplot:
        Transform the abundances in a dictionary format to SYNPLOT format.

    from_synplot:
        Transform the abundances from the SYMPLOT format to a dictionary.

        Parameter
        ---------

        elem: int, str;
            Chemical element. Can be its symbol or its atomic number.

    """
    def  __init__(self, abundance):
        self.abundance = abundance


    def to_synplot(self):
        """
        Writes the Chemical abundances values to SYNPLOT format.
        """

        # If the chemical element is identified with its symbol, swap to the
        #atomic number
        for key in self.abundance:
            if key in PERIODIC:
                self.abundance[PERIODIC[key]] = self.abundance.pop(key)

        # Writes a list with each chemical element and its abundance
        elements = ['{0}, {0}, {1:.2f}'.format(key, val)
                    for key, val in self.abundance.iteritems()]
        assert len(elements) == len(self.abundance)

        # Put into SYNPLOT format
        synplot_format = '[' + ', '.join(elements)+ ']'

        return synplot_format


    def from_synplot(self, element):
        """
        Gets the abundance of a desired chemical element from a string of
        abundances in the SYNPLOT format.
        """

        if type(element) == int:
            atom_n = str(element)
            element = [key for key, val in PERIODIC.iteritems()
                       if val == atom_n][0]
        elif type(element) == str:
            atom_n = str(PERIODIC[element])
        else:
            raise TypeError('The variable `element` should be a string ' +\
                            'or integer.')

        # Gets abundance
        abund = {}
        pattern = re.compile(atom_n + r',\s?' + atom_n + r',\s?(\d+(?:\.\d+)?)')
        match = pattern.search(self.abundance)
        if match:
            abund[element] = float(match.group(1))
        else:
            abund[element] = np.nan

        return abund

#        if len(abund) == 0:
#            raise IndexError('The elementent does not have ' +\
#                             'abundance in the input value.')
#        else:
#            return float(abund[0])

