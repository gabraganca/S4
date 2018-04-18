"""
Plot modules.

"""
#=============================================================================
#Modules
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata


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
