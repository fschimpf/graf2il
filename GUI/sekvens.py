import sys
sys.path.append('../')
from PyQt4 import QtGui, QtCore
from sekvens_gui import Ui_MainWindow
import graf2il

class MeinProgramm(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        XMLFileToCompileName = 'test'
            
        # connect slots for GUI-elements
        self.connect(self.pushButton_2, QtCore.SIGNAL('clicked (bool)'), self.start_graf2il)        
        self.connect(self.pushButton_3, QtCore.SIGNAL('clicked (bool)'), self.chooseInFile)  

        self.statusBar().showMessage('Malvik VGS - Fritz Schimpf') 

    def start_graf2il(self):
        self.statusBar().showMessage('Script graf2il aktiv')
        graf2il.main(self.XMLFileToCompileName,'awl')
        self.statusBar().showMessage('Malvik VGS - Fritz Schimpf')

    def chooseInFile(self):
        self.statusBar().showMessage('Velg inputfil')
        #self.XMLFileToCompileName = str(QtGui.QFileDialog.getOpenFileName(self, 'Velg fil som skal bli oversatt', '', selectedFilter='*.xml'))
        self.XMLFileToCompileName = str(QtGui.QFileDialog.getOpenFileName(self, 'Velg fil som skal bli oversatt', '', 'JGrafchart XML-filer (*.xml);;alle filer (*.*)'))
        self.lineEdit.setText(self.XMLFileToCompileName)
        self.statusBar().showMessage('Malvik VGS - Fritz Schimpf')
        

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

