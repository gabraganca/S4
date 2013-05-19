#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Create and interactive synplot.

I am following the tutorial found at http://zetcode.com/tutorials/pyqt4/
and example from here
http://eli.thegreenplace.net/2009/01/20/matplotlib-with-pyqt-guis/
"""
#==============================================================================

# Import Modules
import sys
from PyQt4 import QtGui, QtCore
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import s4

#==============================================================================

#==============================================================================
# Global variables
FRAME_WIDTH = 760
FRAME_HEIGHT = 480
teff = '20000'
logg = '4'
wstart = '4460'
wend = '4480'


#==============================================================================

#==============================================================================
# 
class Widget(QtGui.QWidget):
    
    def __init__(self):
        super(Widget, self).__init__()

        # set font for tips
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))

        # Frame setup
        self.resize(FRAME_WIDTH, FRAME_HEIGHT)
        self.center()
        self.setWindowTitle('synGUI')
       
        self.create_frame()

        self.teff_textbox.setText(teff) 
        self.logg_textbox.setText(logg) 
        self.wstart_textbox.setText(wstart) 
        self.wend_textbox.setText(wend) 
        self.synplot()
        
    # About    
    def on_about(self):
        msg = """ A GUI for synplot
        
         * describe using ReST
        """
        QtGui.QMessageBox.about(self, "About synGUI", msg.strip())        

    #=========================================================================
    # Core modules
    # synplotmodule    
    def synplot(self):
        global teff, logg, wstart, wend
        # Get parameters
        teff = self.teff_textbox.text()
        logg = self.logg_textbox.text()
        wstart = self.wstart_textbox.text()
        wend = self.wend_textbox.text()
        self.syn = s4.synthesis.synplot(teff, logg, 
                                        wstart = wstart, wend = wend)
        self.syn.run()
        self.on_draw()
    #=========================================================================
    
    #=========================================================================
    # GUI             

    def create_frame(self):

        self.main_frame = QtGui.QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi = self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)  
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)   
        
        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame) 
        
        # Other GUI controls
        #
        # teff
        self.teff_label = QtGui.QLabel('teff')
        self.teff_textbox = self.add_text_input('Enter value for ' + \
                                                'Effective Temperature')
        # logg
        self.logg_label = QtGui.QLabel('logg')
        self.logg_textbox = self.add_text_input('Enter value for ' + \
                                                'logarithm of surface ' + \
                                                'gravity')
        # wstart
        self.wstart_label = QtGui.QLabel('wstart')
        self.wstart_textbox = self.add_text_input('Starting Wavelength')
        # wend
        self.wend_label = QtGui.QLabel('wend')
        self.wend_textbox = self.add_text_input('Ending Wavelength')                                                 
         
        # button to run synplot
        self.run_button = QtGui.QPushButton('Run', self)
        self.run_button.clicked.connect(self.synplot)
        self.run_button.setToolTip('Press to run <b>synplot</b>')
        self.run_button.resize(self.run_button.sizeHint())
        self.run_button.setMaximumWidth(50)

        #
        # Layout with box sizers
        #
        # define grid
        grid = QtGui.QGridLayout()
        #grid.setSpacing(10)
        
        #set canvas
        grid.addWidget(self.canvas, 0, 0, 5, 1)
        grid.addWidget(self.mpl_toolbar, 6, 0)

        # Define first row
        grid.addWidget(self.teff_label, 0, 1)
        grid.addWidget(self.teff_textbox, 0, 2)
        grid.addWidget(self.logg_label, 0, 3)
        grid.addWidget(self.logg_textbox, 0, 4)
        # Define second row
        grid.addWidget(self.wstart_label, 1, 1)
        grid.addWidget(self.wstart_textbox, 1, 2)
        grid.addWidget(self.wend_label, 1, 3)
        grid.addWidget(self.wend_textbox, 1, 4)          
        # Define third row        
        grid.addWidget(self.run_button, 2, 4)
        # set grid  
        self.setLayout(grid) 
        
        #self.setCentralWidget(self.main_frame)
       
        self.show()

    # Draw canvas        
    def on_draw(self):
        """ Redraws the figure
        """
        # clear the axes and redraw the plot anew
        #
        self.axes.clear()        
        
        self.axes.plot(
            self.syn.spectra[:, 0], 
            self.syn.spectra[:, 1])
        
        self.canvas.draw()        
        
    # Set window to center of desktop
    def center(self):
        
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())        
    #=========================================================================
        
    #=========================================================================
    # Support Modules
    
    # add Label + text input
    def add_text_input(self, tip = None, signal = None):
        text_input = QtGui.QLineEdit()
        if tip is not None:
            text_input.setToolTip(tip)
        text_input.setMaximumWidth(55)
        #self.connect(self.logg_textbox, QtCore.SIGNAL('editingFinished ()'),
        #             self.on_draw)         
        return text_input
                 
        
    # ????
    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
        
    # Create (generic) action
    def create_action(self, text, slot = None, shortcut = None, icon = None, 
                      tip = None, checkable = False, signal = "triggered()"):
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
        
    def test(self):
        print 'this is a test' 
    #=========================================================================    
        
#==============================================================================

#==============================================================================
#
def main():
    
    app = QtGui.QApplication(sys.argv)
    wdg = Widget()
    sys.exit(app.exec_()) 
#==============================================================================

#==============================================================================
# 
if __name__ == '__main__':
    main()
#==============================================================================
