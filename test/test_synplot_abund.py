import numpy as np
from s4.synthesis.synplot_abund import Synplot_abund

def test_synplot_abund():
    # Test from dictionary to Synplot format
    assert Synplot_abund({'He': 10.93}).to_synplot() == '[2, 2, 10.93]'
    assert Synplot_abund({'2': 10.93}).to_synplot() == '[2, 2, 10.93]'
    assert Synplot_abund({'He': 10.93, 'O':8.69}).to_synplot() == \
                                                     '[8, 8, 8.69, 2, 2, 10.93]'

    # Test from Synplot format to dictionary
    helium_only = Synplot_abund('[2, 2, 10.93]')
    assert helium_only.from_synplot('He') == {'He':10.93}
    he_o = Synplot_abund('[2, 2, 10.93, 8, 8, 8.69]')
    assert he_o.from_synplot('He') == {'He':10.93}
    assert he_o.from_synplot(2) == {'He':10.93}
    assert he_o.from_synplot(['He', 8]) == {'He': 10.93, u'O': 8.69}
    ## Retrive Nan when there is no element
    assert np.isnan(helium_only.from_synplot('O')['O'])
