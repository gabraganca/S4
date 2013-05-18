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
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
#==============================================================================

#==============================================================================
# 
class Widget(QtGui.QMainWindow):
    
    def __init__(self):
        super(Widget, self).__init__()

        # set font for tips
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))

        # Frame setup
        self.resize(FRAME_WIDTH, FRAME_HEIGHT)
        self.center()
        self.setWindowTitle('synGUI')
        self.create_menu()
        
        self.initUI()

        self.synplot()
        self.on_draw()
        
    # About    
    def on_about(self):
        msg = """ A GUI for synplot
        
         * descride using ReST
        """
        QtGui.QMessageBox.about(self, "About synGUI", msg.strip())        

    # synplotmodule    
    def synplot(self):
        self.syn = s4.synthesis.synplot(20000, 4, wstart = 4460, wend = 4480)
        self.syn.run()    
        
    def initUI(self):

        self.main_frame = QtGui.QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
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
        # button to run synplot
        self.run_button = QtGui.QPushButton('Run', self)
        self.run_button.clicked.connect(self.synplot)
        self.run_button.setToolTip('Press to run <b>synplot</b>')
        self.run_button.resize(self.run_button.sizeHint())
        
        #
        # Layout with box sizers
        # 
        hbox = QtGui.QHBoxLayout()
        
        for w in [self.run_button]:
            hbox.addWidget(w)
            hbox.setAlignment(w, QtCore.Qt.AlignVCenter)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)                  

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
       
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
        
    # Create a menu
    def create_menu(self):
    
        # add File menu
        self.file_menu = self.menuBar().addMenu("&File")
        
        """
        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        """    
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        #self.add_actions(self.file_menu, (load_file_action, None, quit_action))
        self.add_actions(self.file_menu, (None, quit_action))
        
        # add help menu
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About synGUI')
        
        self.add_actions(self.help_menu, (about_action,))       

    # ????
    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
        
    # Create (generic) action
    def create_action(self, text, slot=None, shortcut=None, 
                      icon=None, tip=None, checkable=False, 
                      signal="triggered()"):
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
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
