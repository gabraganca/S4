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
        
        self.initUI()
        
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
        
        self.resize(FRAME_WIDTH, FRAME_HEIGHT)
        self.center()
        self.setWindowTitle('synGUI')
        self.create_menu()
        
        # set font for tips
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        
        # button to run synplot
        run_btn = QtGui.QPushButton('Run', self)
        run_btn.clicked.connect(self.synplot)
        run_btn.setToolTip('Press to run <b>synplot</b> <b>(INACTIVE)</b>')
        run_btn.resize(run_btn.sizeHint())
        run_btn.move(50, 50)
        
    
        self.show()
        
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
