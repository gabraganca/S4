#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create and interactive synplot.

I am following the tutorial found at http://zetcode.com/tutorials/pyqt4/
and example from here
http://eli.thegreenplace.net/2009/01/20/matplotlib-with-pyqt-guis/
"""
#==============================================================================

# Import Modules
import os
import sys
from PyQt4 import QtGui, QtCore
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import numpy as np
import json
import re
from periodic import element
import s4


#==============================================================================

#==============================================================================
# Global variables
FRAME_WIDTH = 1020
FRAME_HEIGHT = 480

HOME_PATH = os.getenv('HOME') + '/'
CONFIG_FILE = HOME_PATH + '.s4_config.json'
ELEMENTS = [element('He'), element('Si')]


#==============================================================================

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # create stuff
        self.wdg = Widget()
        self.setCentralWidget(self.wdg)
        self.createActions()
        self.createMenus()
        #self.createStatusBar()

         # format the main window
        self.resize(FRAME_WIDTH, FRAME_HEIGHT)
        self.center()
        self.setWindowTitle('synGUI')

        # show windows
        self.show()
        self.wdg.show()
        
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())        

    def about(self):
        QtGui.QMessageBox.about(self, self.tr("About synGUI"),
            self.tr("A Graphical User Interface for Synspec.\n" +\
                     u"Created by Gustavo Bragança\n" +\
                     "ga.braganca@gmail.com"))

    def createActions(self):
        self.exitAct = QtGui.QAction(self.tr("E&xit"), self)
        self.exitAct.setShortcut(self.tr("Ctrl+Q"))
        self.exitAct.setStatusTip(self.tr("Exit the application"))
        self.exitAct.triggered.connect(self.close)

        self.aboutAct = QtGui.QAction(self.tr("&About"), self)
        self.aboutAct.setStatusTip(self.tr("Show the application's About box"))
        self.aboutAct.triggered.connect(self.about)

        self.aboutQtAct = QtGui.QAction(self.tr("About &Qt"), self)
        self.aboutQtAct.setStatusTip(self.tr("Show the Qt library's About box"))
        self.aboutQtAct.triggered.connect(QtGui.qApp.aboutQt)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.fileMenu.addAction(self.exitAct)

        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    """
    def createStatusBar(self):
        sb = QtGui.QStatusBar()
        sb.setFixedHeight(18)
        self.setStatusBar(sb)
        self.statusBar().showMessage(self.tr("Ready"))    
    """
#==============================================================================
# 
class Widget(QtGui.QWidget):
    
    def __init__(self):
        super(Widget, self).__init__()

        # set font for tips
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))

        # Frame setup
        #self.resize(FRAME_WIDTH, FRAME_HEIGHT)
        #self.center()
        #self.setWindowTitle('synGUI')

        self.create_frame()
       
        # load config
        try:
            self.load_config()
        except IOError:
            # set up a basic configuration
            self.teff = "20000"
            self.logg = "4"
            self.syn_path = None
            self.parameters = dict(wstart = "4460", wend = "4480", rv = "0",
                                   vrot = "0", vturb = "0", vmac_rt = "0", 
                                   relative = "1", scale = "1", 
                                   abund = '[2, 2, 10.93]')
        
        # set text boxes              
        self.teff_textbox.setText(self.teff) 
        self.logg_textbox.setText(self.logg) 
        self.wstart_textbox.setText(self.parameters['wstart']) 
        self.wend_textbox.setText(self.parameters['wend']) 
        self.rv_textbox.setText(self.parameters['rv'])        
        self.vrot_textbox.setText(self.parameters['vrot'])
        self.vturb_textbox.setText(self.parameters['vturb'])
        self.vmac_textbox.setText(self.parameters['vmac_rt'])
        self.scale_textbox.setText(self.parameters['scale'])
        if 'observ' in self.parameters:
            self.obs_textbox.setText(self.parameters['observ'])
        if self.syn_path is not None:
            self.synspec_textbox.setText(self.syn_path)            

        # set check boxes status
        if self.parameters["relative"] == "0":
            self.norm_cb.setChecked(False)
        else:                                             
            self.norm_cb.setChecked(True)   
            
        # check abundances
        self.abundance_to_textbox()    
        
        self.synplot()

    #=========================================================================
    # Core modules
    # synplotmodule    
    def synplot(self):
        global teff, logg
        # Get and update parameters
        self.teff = self.teff_textbox.text()
        self.logg = float(self.logg_textbox.text())
        self.parameters['wstart'] = self.wstart_textbox.text()
        self.parameters['wend'] = self.wend_textbox.text()
        self.parameters['vrot'] = self.vrot_textbox.text()
        self.parameters['vturb'] = self.vturb_textbox.text()
        self.parameters['vmac_rt'] = self.vmac_textbox.text()
        self.parameters['rv'] = float(self.rv_textbox.text())
        self.parameters['scale'] = float(self.scale_textbox.text())
        if self.obs_textbox.text() != '':
            self.parameters['observ'] = str(self.obs_textbox.text())
        else:
            self.parameters.pop('observ', None)
                
        if self.norm_cb.isChecked():
            self.parameters['relative'] = "1"
        else:
            self.parameters['relative'] = "0"
            
        # check abundance
        self.check_abundance()        
            
        # run synplot
        self.syn = s4.synthesis.Synplot(self.teff, self.logg, 
                                        synplot_path = self.syn_path, 
                                        **self.parameters)
        self.syn.run()
        # make corrections on synthesized spectrum
        self.syn.apply_rvcorr()
        self.syn.apply_scale()
        # draw    
        self.on_draw()
        # save configuration file
        self.save_config()

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
        self.teff_textbox = self.add_text_input('Effective Temperature')
        # logg
        self.logg_label = QtGui.QLabel('logg')
        self.logg_textbox = self.add_text_input('Logarithm of surface ' + \
                                                'gravity')
        # wstart
        self.wstart_label = QtGui.QLabel('wstart')
        self.wstart_textbox = self.add_text_input('Starting Wavelength')
        # wend
        self.wend_label = QtGui.QLabel('wend')
        self.wend_textbox = self.add_text_input('Ending Wavelength')
        # radial velocity
        self.rv_label = QtGui.QLabel('rv')
        self.rv_textbox = self.add_text_input('Radial velocity')        
        # vseni
        self.vrot_label = QtGui.QLabel('vrot')
        self.vrot_textbox = self.add_text_input('Projected rotational ' +\
                                                 'velocity')
        # microturbulent velocity
        self.vturb_label = QtGui.QLabel('vturb')
        self.vturb_textbox = self.add_text_input('Microturbulent velocity')
        # macroturbulent velocity
        self.vmac_label = QtGui.QLabel('vmac_RT')
        self.vmac_textbox = self.add_text_input('Radial-tangential ' + \
                                                 'macroturbulent velocity')
                                                 
        # scale
        self.scale_label = QtGui.QLabel('Scale')
        self.scale_textbox = self.add_text_input('Scale factor')                                                 
        # normalization
        self.norm_cb = QtGui.QCheckBox("Normalization")
        self.norm_cb.setToolTip("If checked, plot normalized spectrum.")
        # Abundance
        self.abund_label = QtGui.QLabel("Abundance")
        self.abund_array = {self.abund_controls(el)[0] : self.abund_controls(el)[1] 
                            for el in ELEMENTS}
        
        # observation file
        # label
        self.obs_label = QtGui.QLabel("Observation file")
        # text edit for observation file path
        self.obs_textbox = self.add_text_input()
        self.obs_textbox.setMaximumWidth(500)
        # button to open file dialog
        self.obs_button = QtGui.QPushButton('Open', self)
        self.obs_button.clicked.connect(self.obs_file_dialog)
        self.obs_button.setToolTip('Open observation file')
        #self.obs_button.resize(self.obs_button.sizeHint())
        self.obs_button.setMaximumWidth(60)
        
        # observation file
        # label
        self.synspec_label = QtGui.QLabel("Synspec path")
        # text edit for observation file path
        self.synspec_textbox = self.add_text_input()
        self.synspec_textbox.setMaximumWidth(500)
        # button to open file dialog
        self.synspec_button = QtGui.QPushButton('Open', self)
        self.synspec_button.clicked.connect(self.synspec_file_dialog)
        self.synspec_button.setToolTip('Open synspec path. If not set, it ' +\
                                       ' will use the S4 default.')
        #self.obs_button.resize(self.obs_button.sizeHint())
        self.synspec_button.setMaximumWidth(60)        
 
        # button to run synplot
        self.run_button = QtGui.QPushButton('Run', self)
        self.run_button.clicked.connect(self.synplot)
        self.run_button.setToolTip('Press to run <b>synplot</b>')
        #self.run_button.resize(self.run_button.sizeHint())
        self.run_button.setMaximumWidth(50)
        

        #
        # Layout with box sizers
        #
        # define grid
        grid = QtGui.QGridLayout()
        #grid.setSpacing(10)
        
        #set matplotlib canvas
        grid.addWidget(self.canvas, 0, 0, 12, 1)
        grid.addWidget(self.mpl_toolbar, 12, 0)

        # row 01
        grid.addWidget(self.teff_label, 0, 1)
        grid.addWidget(self.teff_textbox, 0, 2)
        grid.addWidget(self.logg_label, 0, 3)
        grid.addWidget(self.logg_textbox, 0, 4)
        grid.addWidget(self.wstart_label, 0, 5)
        grid.addWidget(self.wstart_textbox, 0, 6)
        grid.addWidget(self.wend_label, 0, 7)
        grid.addWidget(self.wend_textbox, 0, 8)          
        # row 02
        grid.addWidget(self.rv_label, 1, 1)
        grid.addWidget(self.rv_textbox, 1, 2)        
        grid.addWidget(self.vrot_label, 1, 3)
        grid.addWidget(self.vrot_textbox, 1, 4)   
        grid.addWidget(self.vturb_label, 1, 5)
        grid.addWidget(self.vturb_textbox, 1, 6)
        grid.addWidget(self.vmac_label, 1, 7)
        grid.addWidget(self.vmac_textbox, 1, 8)
        # row 03
        grid.addWidget(self.scale_label, 2, 1)
        grid.addWidget(self.scale_textbox, 2, 2)        
        grid.addWidget(self.norm_cb, 2, 3, 1, 3)
        # row 04
        grid.addWidget(self.abund_label, 3, 1, 1, 2)
        # row 05
        grid.addWidget(self.abund_array[2][0], 4, 1)
        grid.addWidget(self.abund_array[2][1], 4, 2)
        grid.addWidget(self.abund_array[14][0], 4, 3)
        grid.addWidget(self.abund_array[14][1], 4, 4)
        # row 09
        grid.addWidget(self.obs_label, 8, 1, 1, 3)        
        # row 10
        grid.addWidget(self.obs_textbox, 9, 1, 1, 7)
        grid.addWidget(self.obs_button, 9, 8)
        # row 11
        grid.addWidget(self.synspec_label, 10, 1, 1, 3)              
        # row 12
        grid.addWidget(self.synspec_textbox, 11, 1, 1, 7)
        grid.addWidget(self.synspec_button, 11, 8, 1, 1)        
        # row 13        
        grid.addWidget(self.run_button, 12, 8)
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
            self.syn.spectrum[:, 0], 
            self.syn.spectrum[:, 1], label = "Synthetic")
        # plot observation, if availabe
        if 'observ' in self.parameters:
            self.axes.plot(
                self.syn.observation[:, 0],     
                self.syn.observation[:, 1], label = "Observation")                
            self.axes.legend(fancybox = True, loc = 'lower right') 
        
        # set x dimension and label
        xmin = float(self.parameters['wstart'])
        xmax = float(self.parameters['wend'])
        self.axes.set_xlim(xmin, xmax)
        self.axes.set_xlabel(r'Wavelength $(\AA)$')

        # set y dimension and label
        if self.norm_cb.isChecked():
            self.axes.set_ylim(0, 1.05)
            self.axes.set_ylabel('Normalized Flux')
        else:
            self.axes.set_ylabel('Flux')

        # add title
        title  = 'teff = {}, logg = {}, '.format(self.teff, self.logg) + \
                     r'$\xi$ = {}, '.format(self.parameters['vturb']) + \
                     r' vrot = {}, '.format(self.parameters['vrot']) + \
                     r'$\zeta$ = {}, '.format(self.parameters['vmac_rt']) + \
                     r'$\epsilon$ = {}'.format(self.parameters['abund'])
        self.axes.set_title(title, fontsize= 'medium') 
        
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
    def add_text_input(self, tip = None):
        text_input = QtGui.QLineEdit()
        if tip is not None:
            text_input.setToolTip(tip)
        text_input.setMaximumWidth(55) 
        # run synplot if return is pressed
        text_input.returnPressed.connect(self.synplot)
        return text_input
        
    def load_config(self):
        """Load the configuration file"""
        self.parameters = json.load(open(CONFIG_FILE))
        self.teff = self.parameters.pop('teff')
        self.logg = self.parameters.pop('logg')
        if 'syn_path' in  self.parameters: 
            self.syn_path = self.parameters.pop('syn_path')
        
    def save_config(self):
        """Save configuration file"""
        with open(CONFIG_FILE, 'w') as f:
            spam = {key : str(value) for key, value in self.parameters.iteritems()}
            spam.update(dict(teff= str(self.teff), logg= str(self.logg), 
                             syn_path = self.syn_path))
            json.dump(spam, f, sort_keys = True, indent = 4, 
                      separators=(',', ':'))        
        
    def obs_file_dialog(self):
        """Open a file dialog to open observation file"""
        #self.fileDialog = QtGui.QFileDialog(self)
        #self.fileDialog.show()
        fname = str(QtGui.QFileDialog.getOpenFileName(self,"Open File"))
        self.obs_textbox.setText(fname)
        
    def synspec_file_dialog(self):
        """Open a file dialog to get sysnpec _path"""
        #self.fileDialog = QtGui.QFileDialog(self)
        #self.fileDialog.show()
        fname = str(QtGui.QFileDialog.getExistingDirectory(self, 
                                                           "Select Directory"))
        self.synspec_textbox.setText(fname + '/')
        self.syn_path = fname + '/'
        
    def abund_controls(self, element):
        """Return the abundance GUI controls """
        return element.atomic, [QtGui.QLabel(element.symbol), 
                self.add_text_input(element.name + 'abundance')]
                
    def check_abundance(self):
        """Check if abudance is defined"""
        for el, controls in self.abund_array.iteritems():
            if controls[-1].text != '':
                self.textbox_to_abundance()
                break
            
    def textbox_to_abundance(self):
        """Get abundance from textbox and put on synplot format"""
        abund = []
        for el, controls in self.abund_array.iteritems():
            text = controls[-1].text()
            if text != '':
                abund.append('{}, {}, {}'.format(el, el, text))
        
        self.parameters['abund'] = '[' + ', '.join(abund) + ']'               
        
    def abundance_to_textbox(self):
        """Get abundance and write on textbox"""   
        ptrn = '\d+(?:(?=[,\s])|\.\d+)'
        broken_abund = np.array(re.findall(ptrn, self.parameters['abund']))
        # reshape
        broken_abund = broken_abund.reshape([len(broken_abund) / 3, 3])
        for element in broken_abund:
            self.abund_array[int(element[0])][-1].setText(element[-1])
        
    
    """    
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
    
    """    
    def test(self):
        print 'this is a test' 
    #=========================================================================    
        
#==============================================================================

#==============================================================================
#
def main():
    
    app = QtGui.QApplication(sys.argv)
    #wdg = Widget()
    mw = MainWindow()
    sys.exit(app.exec_()) 
#==============================================================================

#==============================================================================
# 
if __name__ == '__main__':
    main()
#==============================================================================
