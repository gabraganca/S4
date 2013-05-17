#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Create and interactive synplot.

I am following the tutorial found at http://zetcode.com/tutorials/pyqt4/
"""
#==============================================================================

# Import Modules
import sys
from PyQt4 import QtGui

#==============================================================================

#==============================================================================
# 
class Widget(QtGui.QWidget):
    
    def __init__(self):
        super(Widget, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        self.setGeometry(600, 200, 640, 480)
        self.setWindowTitle('synGUI')
        
        # set font for tips
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        
        # an temporary empty button
        btn = QtGui.QPushButton('Run', self)
        btn.setToolTip('Press to run <b>synplot</b> <b>(INACTIVE)</b>')
        btn.resize(btn.sizeHint())
        btn.move(50, 50)
    
        self.show()
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
