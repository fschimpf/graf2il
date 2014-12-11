import sys
from PyQt4 import QtGui, QtCore
from sekvens_gui import Ui_MainWindow

class MeinProgramm(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        
        # connect slots for GUI-elements
        self.connect(self.pushButton, QtCore.SIGNAL('clicked ()'), self.startJGrafchart)
        self.connect(self.pushButton_2, QtCore.SIGNAL('clicked (bool)'), self.start_graf2il)        
        self.connect(self.pushButton_3, QtCore.SIGNAL('clicked (bool)'), self.chooseInFile)   

    def startJGrafchart(self):
        self.statusBar().showMessage('starter JGrafchart')

    def start_graf2il(self):
        self.statusBar().showMessage('starter graf2il')

    def chooseInFile(self):
        self.statusBar().showMessage('Velg inputfil')
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Velg fil som skal bli oversatt', '', selectedFilter='*.xml')
        self.lineEdit.setText(fileName)
        

app = QtGui.QApplication(sys.argv)
#locale = QtCore.QLocale.system().name()
locale = "nb_NO"
#locale = "de_DE"
#locale = "en_EN"
#print (locale)
translator = QtCore.QTranslator()
if translator.load("translation_" + locale, "./"):
    app.installTranslator(translator)
programm = MeinProgramm()
programm.show()
sys.exit(app.exec_())   # infinite loop
