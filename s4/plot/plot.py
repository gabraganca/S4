"""
Plot modules.

"""
#=============================================================================
#Modules
import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal
from ..spectra import spectra
#from ..synthesis.synplotwrapper import synplot
from matplotlib.widgets import SpanSelector, Cursor
from matplotlib.mlab import griddata


#=============================================================================

#=============================================================================
# This functions plots the windows.
def plot_windows(windows):
    """ Plots the windows"""
    #Plot the horizontal lines
    for i in range(len(windows)/2):
        plt.hlines(1.025, windows[2*i], windows[2*i+1], colors='b')
    #Plot the vertical dashed lines    
    for i in windows:              
        plt.vlines(i, 0, 1.025, colors='b', linestyles='dashed')
#=============================================================================

#=============================================================================
# This function chooses the windows interactively        
def choose_windows(spectrum, min_wl, max_wl):
    """ Choose the windows interactively"""
    while True:
        if raw_input("Interactive or manual?[I/m]") in ['i', 'I', '']:
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
            axis.hlines(1, min_wl, max_wl, color = 'b', linestyles = 'dashed')
            axis.set_xlim([min_wl, max_wl])
            axis.set_ylim([min(spectra.subselect_spectra                     \
                                   (spectrum, min_wl, max_wl)[1]) - 0.2, 1.05])
            axis.set_xlabel(r'Wavelength $(\AA)$')
            axis.set_ylabel('Normalized Flux')
            span = SpanSelector(axis, onselect, 'horizontal', minspan = 0.05)
            # Plot a vertical line at cursor position
            cursor = Cursor(axis, useblit = True, color = 'red', linewidth = 1 )
            cursor.horizOn = False
            
            plt.show()
            plt.clf()
        
        #Manually input
        else:
            import re
            windows = [float(Decimal("%.2f" %float(i))) 
                for i in re.split('[^0-9. ]', raw_input('Windows = '))[1:-1]]
        
        # Check if Windows are good    
        while True:
            if len(windows) > 0:
                #Check if windows are inside [min_wl, max_wl]
                if min(windows) < min_wl:
                    print 'Chosen windows is below minimum wavelength!'
                    break
                elif max(windows) > max_wl:
                    print 'Chosen windows is above maximum wavelength!'
                    break
                else:
                    #Windows are good.
                    print 'Windows were chosen.\nWindows = ' + str(windows)
                    break    
            else:
                # This will happen only if windows == []
                print 'No Windows will be used.\nWindows = []'
                break
                
        # Give the chance for the user to retry        
        if raw_input('Restart choosing windows?[y/N]') in ['n', 'N', '']:
            plt.close()
            return windows
#=============================================================================

#=============================================================================
# 
def contour_plot(array3d, **kwargs):
    """Do the contour plot of a 3D array. 
    
    Parameters
    ----------
    
    array3d : arra,
        3 dimensional array vector
        
    Optional:
        contour : bool,
            If True, add contours.
        map_name : str,
            Color map name
        xlabel : str,
            label for x-axis.
        ylabel : str,
            label for y-axis.
        title : str,
            Title for plot.
        save_name : str,
            Name for saved file.
          
    """
    n_x = len(np.unique(array3d[:, 0]))
    n_y = len(np.unique(array3d[:, 1]))
    
    X = np.reshape(array3d[:, 0], (n_x, n_y)) 
    Y = np.reshape(array3d[:, 1], (n_x, n_y))
    Z = np.reshape(array3d[:, 2], (n_x, n_y))
    
    #Do contour plot
    plt.figure()
    CS = plt.contour(X, Y, Z)
    plt.clabel(CS, inline = 1, fontsize = 10)
    if kwargs.has_key('xlabel'): 
        plt.xlabel(kwargs['xlabel'])
    if kwargs.has_key('ylabel'):
        plt.ylabel(kwargs['ylabel'])
    if kwargs.has_key('title'):
        plt.title(kwargs['title'])        

    if kwargs.has_key('save'):
        plt.savefig(kwargs['save'])
    else:        
        plt.savefig('contour.pdf')
    plt.clf()
#=============================================================================
    
#=============================================================================
# 
def color_map_plot(X_vector, Y_vector, Z_vector, num = 100, **kwargs):
    """
    Do a color map of a X, Y, Z vector. 
    
    Parameters
    ----------
    
    X_vector : list,
        x-axis vector
    Y_vector : list,
        y-axis vector
    Z_vector :
        color-axis vector
    num : int, optional
        Number of samples to generate. Default is 100.        
        
    Optional:
        contour : bool,
            If True, add contours.
        map_name : str,
            Color map name
        xlabel : str,
            label for x-axis.
        ylabel : str,
            label for y-axis.
        bar_label : str,
            label for color bar
        title : str,
            Title for plot.
        save_name : str,
            Name for saved file.
      
        
    Adapted from Anderson Ribeiro code.
    """

    xi = np.linspace(min(X_vector), max(X_vector), num)    
    yi = np.linspace(min(Y_vector), max(Y_vector), num)
    zi = griddata(X_vector, Y_vector, Z_vector, xi, yi)

    #Do contour plot
    if 'contour' in kwargs:        
        plt.contour(xi, yi, zi, linewidths = 0.5, colors = 'k')
    if 'map_name' in kwargs:        
        map_id = plt.get_cmap(kwargs['map_name'])
    else:
        map_id = None
        
    plt.pcolormesh(xi, yi, zi, cmap = map_id)
    cbar = plt.colorbar() 
    cbar.set_label(kwargs['bar_label'])
    
    if kwargs.has_key('xlabel'): 
        plt.xlabel(kwargs['xlabel'])
    if kwargs.has_key('ylabel'):
        plt.ylabel(kwargs['ylabel'])
    if kwargs.has_key('title'):
        plt.title(kwargs['title'])        

    if kwargs.has_key('save_name'):
        plt.savefig(kwargs['save_name'])
    else:        
        plt.savefig('color_map.pdf')
    plt.clf()
#=============================================================================    
    
'''   
#=============================================================================
# Contruct a spectral line intensity contour plot   

def flux_countour_plot(spec_line, **kwargs):
    """Contruct a contour plot of the spectral line flux."""

    teff_range = range(15000, 30000, 500)
    logg_range = np.arange(3.5, 4.6, 0.1)
    for i, grav in enumerate(logg_range):
        if int(10*grav) == 45:
            logg_range[i] = 4.499
    
    int_storage = np.zeros([len(teff_range)*len(logg_range), 3])

    #Set some synplot defaults
    kwargs['noplot'] = 1
    kwargs['relative'] = 1
    
    for count, pair in                                                      \
                 enumerate([[i,j] for i in teff_range for j in logg_range]):
        #Prepare for synplot
        kwargs['teff'] = pair[0]
        kwargs['logg'] = pair[1]
        kwargs['wstart'] = spec_line - 30
        kwargs['wend'] = spec_line + 30
        # Calculate the spectra
        spec = synplot(**kwargs)
        spec.run()
        #Find the intensity          
        int_storage[count] = pair[0], pair[1],                               \
                              spectra.line_position(spec.spectra,            \
                                                    spec_line)[1]
        #print count,pair[0],pair[1], int_storage[count,2]
    
    #Do the contour plot
    contour_plot(int_storage, xlabel = 'Teff', ylabel = 'logg',             \
                 title = str(spec_line)+r' $\AA$',                          \
                 save = 'contour_'+str(spec_line)+'.pdf')               
    
    if kwargs.has_key('return'):    
        return int_storage

#=============================================================================
'''