# -*- coding: utf-8 -*-
"""
This module contains all functions that allow the user to choose windows on a 
pre-defined spectrum and to plot the windows on a spectrum.

@author: gbra
"""

import matplotlib.pyplot as plt
from decimal import Decimal
from ..spectra import spectra
from matplotlib.widgets import SpanSelector, Cursor


# This functions plots the windows.
def plot_windows(windows):
    """
    Plots the windows
    
    Parameters
    ---------

    windows: list:
        position of the beggining and the end of the list.
    """
    #Plot the horizontal lines
    for i in range(len(windows)/2):
        plt.hlines(1.025, windows[2*i], windows[2*i+1], colors='b')
    #Plot the vertical dashed lines    
    for i in windows:              
        plt.vlines(i, 0, 1.025, colors='b', linestyles='dashed')


def choose_windows(spectrum, wstart, wend):
    """ 
    Choose the windows interactively

    Parameters
    ----------

    spectrum: array;
        Bi-dimensional array containing the spectrum. First column should be 
        wavelength and the second, flux.
        
    wstart: int, float;
        Starting wavelength.
        
    wend: int, float;
        Ending wavelength.
    """
    
    #Define function that will obtain the cursor x position
    def onselect(vmin, vmax):
        """ Function that will obtain the cursor x position"""
        windows.append(float(Decimal("%.2f" % vmin)))
        windows.append(float(Decimal("%.2f" % vmax)))
        plot_windows(windows)
        plt.draw()
    #Create a plot so the user can choose the windows    
    windows = []                            #Set an empty window
    axis = plt.subplot(111)
    axis.plot(spectrum[:, 0], spectrum[:, 1], 'k-')
    axis.hlines(1, wstart, wend, color = 'b', linestyles = 'dashed')
    axis.set_xlim([wstart, wend])
    axis.set_ylim([min(spectra.subselect_spectra                     \
                           (spectrum, wstart, wend)[1]) - 0.2, 1.05])
    axis.set_xlabel(r'Wavelength $(\AA)$')
    axis.set_ylabel('Normalized Flux')
    span = SpanSelector(axis, onselect, 'horizontal', minspan = 0.05)
    # Plot a vertical line at cursor position
    cursor = Cursor(axis, useblit = True, color = 'red', linewidth = 1 )
    cursor.horizOn = False
    
    plt.show()
    plt.clf()
    
  
