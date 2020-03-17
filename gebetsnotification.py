"""
cd windows_ordner\documents\python files
python gebetsnotification.py
"""
import plyer
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import time

#plyer.notification.notify(message="hello",title="test")


class Notification(QtWidgets.QMainWindow):
    def __init__(self,message):
        self.message=message
        super().__init__()
        self.init()
    def init(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet("""QMainWindow{background-color: rgb(32,32,32);}""")
        self.setGeometry(1000,675,350,80)
        
        self.titlewidget=QtWidgets.QLabel("test")
        newfont = QtGui.QFont("Times", 11,QtGui.QFont.Bold) 
        self.titlewidget.setFont(newfont)
        self.titlewidget.setStyleSheet("""color: white;""")
        
        
        self.picturewidget=QtWidgets.QLabel()
        self.pixmap = QtGui.QPixmap("K_5.png")
        pixmap2=self.pixmap.scaledToWidth(70)
        self.pixmap3=pixmap2.scaledToHeight(70)
        self.picturewidget.setPixmap(self.pixmap3)
        self.picturewidget.move(0,0)
        
        self.messagewidget=QtWidgets.QLabel(self.message)
        newfont = QtGui.QFont("Times", 11) 
        self.messagewidget.setFont(newfont)
        self.messagewidget.setStyleSheet("""color: gray;""")
        
        self.textlayout = QtWidgets.QVBoxLayout()
        self.textlayout.addWidget(self.titlewidget)
        self.textlayout.addWidget(self.messagewidget)
        self.textlayout.addStretch(1)
        
        self.contentlayout = QtWidgets.QHBoxLayout()
        self.contentlayout.addWidget(self.picturewidget)
        self.contentlayout.addLayout(self.textlayout)
        self.contentlayout.addStretch(1)
        
        self.contentwidget = QtWidgets.QWidget()
        self.contentwidget.setLayout(self.contentlayout)
        
        self.setCentralWidget(self.contentwidget)
        self.show()

if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Notification("hello")
    #w.show()
    sys.exit(app.exec_())