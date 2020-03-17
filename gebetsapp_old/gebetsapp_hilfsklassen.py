# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 15:24:39 2018

@author: DELL
"""

import MySQLdb
import sys
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

conn = MySQLdb.connect(host="localhost",user="josua",password="Immanueljan1?",db="information_schema")
c = conn.cursor()
c.execute("USE gebetsapp2")

class BeteFenster(QMainWindow):
    def __init__(self,ID):
        super().__init__()
        self.ID=ID
        self.init()
    def init(self):
        self.setGeometry(300,300,300,100)
        self.setWindowIcon(QIcon("beten.jpg"))
        conn.commit()
        c.execute("SELECT person_id FROM personen")
        a = c.fetchall()
        idlist=[]
        for i in a:
            idlist.append(i[0])
        if self.ID not in idlist:
            self.ID = max(idlist)
        c.execute("SELECT vorname FROM personen WHERE person_id = {}".format(self.ID))
        a = c.fetchall()
        self.vorname=a[0][0]
        c.execute("SELECT nachname FROM personen WHERE person_id = {}".format(self.ID))
        self.nachname=c.fetchall()[0][0]
        if self.nachname:
            self.setWindowTitle("Beten für {} {}".format(self.vorname,self.nachname))
        else:
            self.setWindowTitle("Beten für {}".format(self.vorname))

        c.execute("""SELECT anliegen FROM gebete 
                  WHERE person_id = {} AND gebetsart = "Bitte" """.format(self.ID))
        self.bitteanliegen=c.fetchall()[0]
        
        c.execute("""SELECT anliegen FROM gebete 
                  WHERE person_id = {} AND gebetsart = "Danke" """.format(self.ID))
        self.dankeanliegen=c.fetchall()[0]
        
        
        self.bittelayout=QHBoxLayout()
        self.blabelteil=QVBoxLayout()
        self.blabelteil.addWidget(QLabel("Bitte:"))
        self.blabelteil.addStretch(1)
        self.bittelayout.addLayout(self.blabelteil)
        self.bitteteil=QHBoxLayout()
        for i in self.bitteanliegen:
            self.bitteteil.addWidget(QLabel(i))
        if len(self.bitteanliegen)==0:
            self.bitteteil.addWidget(QLabel("-"))
        self.bittelayout.addLayout(self.bitteteil)
        
        self.dankelayout=QHBoxLayout()
        self.dlabelteil=QVBoxLayout()
        self.dlabelteil.addWidget(QLabel("Danke:"))
        self.dlabelteil.addStretch(1)
        self.dankelayout.addLayout(self.dlabelteil)
        self.danketeil=QHBoxLayout()
        for i in self.dankeanliegen:
            self.danketeil.addWidget(QLabel(i))
        if len(self.dankeanliegen)==0:
            self.danketeil.addWidget(QLabel("-"))
        self.dankelayout.addLayout(self.danketeil)
        
        
        widget=QWidget()
        vbox=QVBoxLayout()
        vbox.addLayout(self.bittelayout)
        vbox.addLayout(self.dankelayout)
        widget.setLayout(vbox)
        self.setCentralWidget(widget)
        
        self.show()

class InputLayout(QHBoxLayout):
    def __init__(self, frage, PlaceHolderText = None, InputMask = None):
        super().__init__()
        self.frage = frage
        self.PlaceHolderText = PlaceHolderText
        self.InputMask = InputMask
        self.init()
    
    def init(self):
        label=QLabel(self.frage)
        self.addWidget(label)
        self.Input = QLineEdit()
        if self.PlaceHolderText!=None:
            self.Input.setPlaceholderText(self.PlaceHolderText)
#        if self.InputMask!=None:
#            self.Input.setInputMask(self.InputMask)
        self.addWidget(self.Input)
        
class TextLayout(QHBoxLayout):
    def __init__(self,frage):
        super().__init__()
        self.frage = frage
        self.init()
    def init(self):
        fragelabel = QLabel(self.frage)
        frageteil = QVBoxLayout()
        frageteil.addWidget(fragelabel)
        frageteil.addStretch(1)
        self.textedit = QTextEdit()
        self.addLayout(frageteil)
        self.addWidget(self.textedit)