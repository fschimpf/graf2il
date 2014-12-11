import sys
from PyQt4 import QtGui, QtCore
from sekvens_gui import Ui_MainWindow

class MeinProgramm(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        
        # connect slots for GUI-elements
        #self.connect(self.pushButton, QtCore.SIGNAL('clicked ()'), self.on_send_serial_command)
        #self.connect(self.pushButton_2, QtCore.SIGNAL('clicked (bool)'), self.toggle_SlowPWM)        
        #self.connect(self.checkBox, QtCore.SIGNAL('clicked (bool)'), self.activateAutoADCReload)   


app = QtGui.QApplication(sys.argv)
#locale = QtCore.QLocale.system().name()
locale = "nb_NO"
#locale = "de_DE"
#locale = "en_EN"
print (locale)
translator = QtCore.QTranslator()
if translator.load("translation_" + locale, "./"):
    app.installTranslator(translator)
programm = MeinProgramm()
programm.show()
sys.exit(app.exec_())   # infinite loop
self.ser.close()        # close serial port
