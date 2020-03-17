"""
cd windows_ordner/documents/python files/gebetsapp
python gebetsapp2.py
"""

import sqlite3
import sys
import datetime
import random
from PyQt5.QtWidgets import QLabel,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QPushButton,QLineEdit,QScrollArea,QTabWidget,QApplication
from PyQt5.QtGui import QIcon,QFont,QPixmap
from PyQt5.QtCore import Qt,QTimer
import sip
import gebetsapp_hilfsklassen2

conn = sqlite3.connect("gebetsapp_test.db")
c = conn.cursor()

def setup():
    c.execute("""CREATE TABLE IF NOT EXISTS personen (
    person_id INTEGER PRIMARY KEY,
    nachname VARCHAR(50) default null,
    vorname VARCHAR(50) not null,
    geburtsdatum date default null
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS gebete (
    gebets_id INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL,
    gebetsart VARCHAR(5) NOT NULL,
    anliegen VARCHAR(1000) NOT NULL
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS oldidlist (
    ID INTEGER NOT NULL        
    )""")
    conn.commit()
    

class Row(QGridLayout):
    def __init__(self,person):
        super().__init__()
        self.person=person
        self.init()
        
    def init(self):
        for n,item in enumerate(self.person[:-1]):
            self.addWidget(QLabel(str(item)),0,n*2,1,2)
            self.n=n
        betenButton=QPushButton("Beten")
        self.ID=self.person[-1]
        betenButton.clicked.connect(self.beten)
        bearbeitenButton = QPushButton("Bearbeiten")
        bearbeitenButton.clicked.connect(self.bearbeiten)
        self.addWidget(betenButton,0,n*2+2,1,1)
        self.addWidget(bearbeitenButton,0,n*2+3,1,1)
        
    def beten(self):
        self.b = gebetsapp_hilfsklassen2.BeteFenster(self.ID)
    
    def bearbeiten(self):
        gebetsliste=[]
        artenliste=["Bitte","Danke"]
        for art in artenliste:
            c.execute("""SELECT anliegen FROM gebete 
                      WHERE person_id={} 
                      AND gebetsart="{}" """.format(self.ID,art))
            gebetsliste.append(c.fetchall()[0][0])
        self.a = addPersonDialog( 
                        vorname = self.person[1], 
                        nachname = self.person[0], 
                        geburtsdatum = self.person[2], 
                        gebetsanliegen = gebetsliste,
                        ersetzen = True,
                        replace_id = self.ID)
        
class addPersonDialog(QMainWindow):
    def __init__(self, 
                 warning = None, 
                 vorname = None, 
                 nachname = None, 
                 geburtsdatum = None, 
                 gebetsanliegen = None, 
                 ersetzen = None, 
                 replace_id = None):
        super().__init__()
        #self.parent = parent
        self.warning = warning
        self.vornamentext = vorname
        self.nachnamentext = nachname
        self.geburtsdatumstext = geburtsdatum
        self.gebetsanliegenliste = gebetsanliegen
        self.ersetzen = ersetzen
        self.replace_id = replace_id
        self.init()
        
    def init(self):
        self.setWindowTitle("Person hinzufügen")
        self.setWindowIcon(QIcon("beten.jpg"))
        self.setGeometry(300,300,300,300)
        w = QWidget()
        self.vorname = gebetsapp_hilfsklassen2.InputLayout("Vorname:*")
        if self.vornamentext:
            self.vorname.Input.setText(self.vornamentext)
        self.nachname = gebetsapp_hilfsklassen2.InputLayout("Nachname:")
        if self.nachnamentext:
            self.nachname.Input.setText(self.nachnamentext)
        self.geburtsdatum = gebetsapp_hilfsklassen2.InputLayout("Geburtsdatum:",
                                                               PlaceHolderText="JJJJ-MM-TT",
                                                               InputMask="9999-99-99")
        if self.geburtsdatumstext!=None:
            self.geburtsdatum.Input.setText(str(self.geburtsdatumstext))
        self.bitte = gebetsapp_hilfsklassen2.TextLayout("Bitte")
        self.danke = gebetsapp_hilfsklassen2.TextLayout("Danke")
        if self.gebetsanliegenliste:
                self.bitte.textedit.setPlainText(self.gebetsanliegenliste[0])
                self.danke.textedit.setPlainText(self.gebetsanliegenliste[1])
            
        
        
        buttons = QHBoxLayout()
        abbruch = QPushButton("Abbrechen")
        abbruch.clicked.connect(self.destroy)
        ok = QPushButton("Ok")
        ok.clicked.connect(self.addPerson)
        buttons.addWidget(abbruch)
        buttons.addStretch(1)
        if self.ersetzen and self.replace_id:
            remove = QPushButton("Person entfernen")
            remove.clicked.connect(self.remove)
            buttons.addWidget(remove)
            buttons.addStretch(1)
        buttons.addWidget(ok)
        
        vbox = QVBoxLayout()
        if self.warning:
            warninglabel=QLabel(self.warning)
            warninglabel.setStyleSheet(".QLabel { color:red }")
            vbox.addWidget(warninglabel)
        vbox.addLayout(self.vorname)
        vbox.addLayout(self.nachname)
        vbox.addLayout(self.geburtsdatum)
        vbox.addWidget(QLabel("Gebetsanliegen:"))
        vbox.addLayout(self.bitte)
        vbox.addLayout(self.danke)
        vbox.addLayout(buttons)
        
        w.setLayout(vbox)
        self.setCentralWidget(w)
        self.show()
        
    def remove(self):
        c.execute("""DELETE FROM personen WHERE person_id={}""".format(self.replace_id))
        c.execute("""DELETE FROM gebete WHERE person_id={}""".format(self.replace_id))
        conn.commit()
        if w.tab1.suche:
            w.tab1.breaksearch()
        else:
            w.tab1.updatedata()
        self.destroy()
        
    def addPerson(self):
        self.vornamentext = self.vorname.Input.text()
        self.nachnamentext = self.nachname.Input.text()
        self.geburtsdatumstext = self.geburtsdatum.Input.text()
        self.gebetsanliegenliste = []
        a = self.bitte.textedit.toPlainText()
        if a!=None:
            self.gebetsanliegenliste.append(a)
        else:
            self.gebetsanliegenliste.append("")
            
        a = self.danke.textedit.toPlainText()    
        if a!=None:
            self.gebetsanliegenliste.append(a)
        else:
            self.gebetsanliegenliste.append("")
        self.destroy()
        
        if self.ersetzen and self.replace_id:
            c.execute("""DELETE FROM personen WHERE person_id={}""".format(self.replace_id))
            c.execute("""DELETE FROM gebete WHERE person_id={}""".format(self.replace_id))
            conn.commit()
        if self.validate(self.geburtsdatumstext,self.vornamentext,self.nachnamentext):
            if self.nachnamentext and self.geburtsdatumstext:
                c.execute("""INSERT INTO personen(nachname,vorname,geburtsdatum) 
                VALUES("{}","{}","{}")""".format(self.nachnamentext,self.vornamentext,self.geburtsdatumstext))
                conn.commit()
            elif not self.nachnamentext and self.geburtsdatumstext:
                c.execute("""INSERT INTO personen(vorname,geburtsdatum) 
                VALUES("{}","{}")""".format(self.vornamentext,self.geburtsdatumstext))
                conn.commit()
            elif self.nachnamentext and not self.geburtsdatumstext:
                c.execute("""INSERT INTO personen(nachname,vorname) 
                VALUES("{}","{}")""".format(self.nachnamentext,self.vornamentext))
                conn.commit()
            else:
                c.execute("""INSERT INTO personen(vorname) 
                VALUES("{}")""".format(self.vornamentext))
                conn.commit()
            c.execute("""SELECT MAX(person_id) FROM personen""")
            ID=int(c.fetchall()[0][0])
            
            c.execute("""INSERT INTO gebete(person_id,gebetsart,anliegen) 
            VALUES ("{}","{}","{}")""".format(ID,"Bitte",self.gebetsanliegenliste[0]))
            
            c.execute("""INSERT INTO gebete(person_id,gebetsart,anliegen) 
            VALUES ("{}","{}","{}")""".format(ID,"Danke",self.gebetsanliegenliste[1]))   
            
            conn.commit()
            #w.tab1.updatedata()
            if w.tab1.suche:
                w.tab1.breaksearch()
            else:
                w.tab1.updatedata()
        
    def validate(self,date_text,vornamen_text,nachnamen_text):
        if date_text != "":
            try:
                datetime.datetime.strptime(date_text, '%Y-%m-%d')
            except ValueError:
                addPersonDialog(#self.parent, 
                                warning="Achtung!\nBitte gültiges Geburtsdatum im Format JJJJ-MM-TT angeben", 
                                vorname = self.vornamentext, nachname=self.nachnamentext,
                                geburtsdatum=self.geburtsdatumstext, 
                                gebetsanliegen=self.gebetsanliegenliste)
                return False
        if vornamen_text=="":
            addPersonDialog(#self.parent, 
                            warning="Achtung!\nDer Vorname darf nicht leerbleiben!", 
                            vorname = self.vornamentext,
                            nachname=self.nachnamentext,
                            geburtsdatum=self.geburtsdatumstext, 
                            gebetsanliegen=self.gebetsanliegenliste)
            return False
        if len(vornamen_text)>20:
            addPersonDialog(#self.parent, 
                            warning="Achtung!\nDer Vorname darf maximal 20 Stellen lang sein!", 
                            vorname = self.vornamentext,
                            nachname=self.nachnamentext,
                            geburtsdatum=self.geburtsdatumstext, 
                            gebetsanliegen=self.gebetsanliegenliste)
            return False
        if len(nachnamen_text)>20:
            addPersonDialog(#self.parent, 
                            warning="Achtung!\nDer Nachname darf maximal 20 Stellen lang sein!", 
                            vorname = self.vornamentext,
                            nachname=self.nachnamentext,
                            geburtsdatum=self.geburtsdatumstext, 
                            gebetsanliegen=self.gebetsanliegenliste)
            return False
        return True

        
class Notification(QMainWindow):
    def __init__(self,message = None, ID = None):
        self.message=message
        self.ID = ID
        super().__init__()
        self.init()
        
    def init(self):
        if self.ID != None:
            c.execute("""SELECT vorname,nachname FROM personen WHERE person_id = {}""".format(self.ID))
            a = c.fetchall()
            self.vorname = a[0][0]
            self.nachname = a[0][1]
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""QMainWindow{background-color: rgb(32,32,32);}""")
        self.setGeometry(1000,675,350,80)
        
        self.titlewidget=QLabel("Gebetsapp")
        newfont = QFont("Times", 11,QFont.Bold) 
        self.titlewidget.setFont(newfont)
        self.titlewidget.setStyleSheet("""color: white;""")
        
        
        self.picturewidget=QLabel()
        self.pixmap = QPixmap("beten.jpg")
        pixmap2=self.pixmap.scaledToWidth(70)
        self.pixmap3=pixmap2.scaledToHeight(70)
        self.picturewidget.setPixmap(self.pixmap3)
        self.picturewidget.move(0,0)
        
        if self.ID!= None:
            if self.nachname != None:
                self.messagewidget=QLabel("Bete für {} {}".format(self.vorname, self.nachname))
            else:
                self.messagewidget=QLabel("Bete für {}".format(self.vorname))
        else:
            self.messagewidget=QLabel(self.message)
            
        newfont = QFont("Times", 11) 
        self.messagewidget.setFont(newfont)
        self.messagewidget.setStyleSheet("""color: gray;""")
        
        self.textlayout = QVBoxLayout()
        self.textlayout.addWidget(self.titlewidget)
        self.textlayout.addWidget(self.messagewidget)
        self.textlayout.addStretch(1)
        
        self.contentlayout = QHBoxLayout()
        self.contentlayout.addWidget(self.picturewidget)
        self.contentlayout.addLayout(self.textlayout)
        self.contentlayout.addStretch(1)
        
        self.contentwidget = QWidget()
        self.contentwidget.setLayout(self.contentlayout)
        
        self.setCentralWidget(self.contentwidget)
        self.show()
        
        
    def mousePressEvent(self,event):
        self.click()

    def click(self):
        self.destroy()
        if self.ID != None:
            w.a = gebetsapp_hilfsklassen2.BeteFenster(self.ID)
        else:
            w.setWindowState(w.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
            w.activateWindow()

    
    
class Personenfenster(QWidget):
    def __init__(self):
        super().__init__()
        self.init()
        self.suche=False
    
    def string2list(self,tupel):
        retlist=[]
        for index in range(len(tupel)):
            string = tupel[index][0]
            retlist.append(string)
        return retlist

    def init(self):
        #Daten aus der Datenbank
        c.execute("SELECT nachname FROM personen")
        nachnamenlistealsstring=c.fetchall()
        c.execute("SELECT vorname FROM personen")
        vornamenlistealsstring=c.fetchall()
        c.execute("SELECT geburtsdatum FROM personen")
        geburtsdatenlistealsstring=c.fetchall()
        c.execute("SELECT person_id FROM personen")
        idlistealsstring=c.fetchall()
        
        
        nachnamenliste = self.string2list(nachnamenlistealsstring)
        vornamenliste = self.string2list(vornamenlistealsstring)
        geburtsdatenliste = self.string2list(geburtsdatenlistealsstring)
        idliste = self.string2list(idlistealsstring)
        
        self.scrollmatrix = []
        for index,item in enumerate(vornamenliste):
            self.scrollmatrix.append([nachnamenliste[index],item,
                                      geburtsdatenliste[index],idliste[index]])
        
        #Suchenfeld
        self.Input = QLineEdit(self)
        self.Input.setPlaceholderText("Suchen...")
        self.Input.returnPressed.connect(self.Inputtext)
        
        #+-Button
        self.AddButton = QPushButton("+")
        self.AddButton.clicked.connect(self.addPerson)
        
        self.clearButton = QPushButton("reset")
        self.clearButton.clicked.connect(self.clear)
   
        #HBox mit dem Suchen Feld ganz links und dem +-Button ganz rechts
        self.suchen = QHBoxLayout()
        self.suchen.addWidget(self.Input)
        self.suchen.addStretch(1)
        #self.suchen.addWidget(self.clearButton)
        self.suchen.addWidget(self.AddButton)
        
        #HBox mit den Überschriften für die einzelnen Zeilen:
        self.row0 = QGridLayout()
        self.row0.addWidget(QLabel("Nachname"),0,0,1,2)
        self.row0.addWidget(QLabel("Vorname"),0,2,1,2)
        self.row0.addWidget(QLabel("Geburtsdatum"),0,4,1,2)
        self.row0.addWidget(QLabel("Beten/Bearbeiten"),0,6,1,2)
        
        #Hier kommt die Personenanzeige 
        self.scroll = QScrollArea()
        self.personenanzeige = QWidget()
        self.scroll.setWidgetResizable(True)
        
        #Hier kommen die Personen
        
        self.personenanzeigenLayout = QVBoxLayout(self.personenanzeige)
        for person in self.scrollmatrix:
            self.personenanzeigenLayout.addLayout(Row(person))
        self.personenanzeigenLayout.addStretch(1)
        self.personenanzeige.setLayout(self.personenanzeigenLayout)
        self.scroll.setWidget(self.personenanzeige)
        
        #setzt alles in eine große VBox
        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.suchen)
        self.vbox.addLayout(self.row0)
        self.vbox.addWidget(self.scroll)
        self.setLayout(self.vbox)
    
    def Inputtext(self):
        text1 = self.Input.text()
        if text1!=None and text1!="":
            text1=str(text1)
            c.execute("SELECT nachname FROM personen")
            nachnamenlistealsstring=c.fetchall()
            c.execute("SELECT vorname FROM personen")
            vornamenlistealsstring=c.fetchall()
            c.execute("SELECT geburtsdatum FROM personen")
            geburtsdatenlistealsstring=c.fetchall()
            c.execute("SELECT person_id FROM personen")
            idlistealsstring=c.fetchall()
    
            nachnamenliste = self.string2list(nachnamenlistealsstring)
            vornamenliste = self.string2list(vornamenlistealsstring)
            geburtsdatenliste = self.string2list(geburtsdatenlistealsstring)
            idliste = self.string2list(idlistealsstring)
            
            searchednachname=[]
            for nachname in nachnamenliste:
                if nachname:
                    if text1 in nachname:
                        searchednachname.append(nachname)
            
            searchedvorname=[]
            for vorname in vornamenliste:
                if vorname:
                    if text1 in vorname:
                        searchedvorname.append(vorname)
            idliste=[]
            searchednachname=list(set(searchednachname))
            searchedvorname=list(set(searchedvorname))
            
            for i in searchednachname:
                c.execute("""SELECT person_id FROM personen WHERE nachname="{}" """.format(i))
                a=c.fetchall()
                for j in a:
                    idliste.append(j[0])
        
            for i in searchedvorname:
                c.execute("""SELECT person_id FROM personen WHERE vorname="{}" """.format(i))
                a=c.fetchall()
                for j in a:
                    idliste.append(j[0])
            idliste=list(set(idliste))
            if len(idliste)>0:
                nachnamenliste=[]
                vornamenliste=[]
                geburtsdatenliste=[]
                for i in idliste:
                    c.execute("""SELECT nachname FROM personen WHERE person_id={}""".format(i))
                    nachnamenliste.append(c.fetchall()[0][0])
                    c.execute("""SELECT vorname FROM personen WHERE person_id={}""".format(i))
                    vornamenliste.append(c.fetchall()[0][0])
                    c.execute("""SELECT geburtsdatum FROM personen WHERE person_id={}""".format(i))
                    geburtsdatenliste.append(c.fetchall()[0][0])
                
                #Neugestaltung mit gesuchten Werten
                self.scrollmatrix = []
                for index,item in enumerate(vornamenliste):
                    self.scrollmatrix.append([nachnamenliste[index],item,
                                              geburtsdatenliste[index],idliste[index]])
                    
                self.vbox.removeWidget(self.scroll)
                self.scroll.close()
                
                #Hier kommt die Personenanzeige 
                self.scroll = QScrollArea()
                self.personenanzeige = QWidget()
                self.scroll.setWidgetResizable(True)
                
                #Hier kommen die Personen
                self.personenanzeigenLayout = QVBoxLayout(self.personenanzeige)
                for person in self.scrollmatrix:
                    self.personenanzeigenLayout.addLayout(Row(person))
                self.personenanzeigenLayout.addStretch(1)
                self.personenanzeige.setLayout(self.personenanzeigenLayout)
                self.scroll.setWidget(self.personenanzeige)
                
                self.vbox.addWidget(self.scroll)
                self.vbox.update()
            else:
                self.vbox.removeWidget(self.scroll)
                self.scroll.close()
                noresults = QWidget()
                noresultslayout=QVBoxLayout()
                noresultslabel=QLabel("""Zu diesem Suchbegriff wurden leider keine Ergebnisse gefunden\n
Versuchen Sie es mit einem anderen Suchbegriff oder fügen Sie die gesuchte Person hinzu""")
                noresultslabel.setAlignment(Qt.AlignCenter)
                noresultslayout.addWidget(noresultslabel)
                noresults.setLayout(noresultslayout)
                self.scroll = QScrollArea()
                self.scroll.setWidget(noresults)
                self.vbox.addWidget(self.scroll)
                self.vbox.update()
            
            self.suchen.removeWidget(self.AddButton)
            #self.suchen.removeWidget(self.clearButton)
            if not self.suche:
                self.breaksearchButton=QPushButton("Suche abbrechen")
                self.breaksearchButton.clicked.connect(self.breaksearch)
                self.suchen.addWidget(self.breaksearchButton)
                self.suche=True
            #self.suchen.addWidget(self.clearButton)
            self.suchen.addWidget(self.AddButton)
            self.suchen.update()
    
    def breaksearch(self):
        self.suchen.removeWidget(self.breaksearchButton)
        self.suche=False
        self.breaksearchButton.close()
        self.Input.setText("")
        self.suchen.update()
        self.updatedata()

    def clear(self):
        c.execute("DROP TABLE IF EXISTS personen")
        c.execute("""CREATE TABLE IF NOT EXISTS personen (
    person_id INT(10) NOT NULL AUTO_INCREMENT,
    nachname VARCHAR(50) default null,
    vorname VARCHAR(50) not null,
    geburtsdatum date default null,
    primary key (person_id))""")
        
        c.execute("DROP TABLE IF EXISTS gebete")
        c.execute("""CREATE TABLE IF NOT EXISTS gebete (
    gebets_id INT(10) NOT NULL AUTO_INCREMENT,
    person_id INT(10) NOT NULL,
    gebetsart VARCHAR(5) NOT NULL,
    anliegen VARCHAR(1000) NOT NULL,
    PRIMARY KEY (gebets_id)
    )""")
        
        c.execute("DROP TABLE IF EXISTS oldidlist")
        c.execute("""CREATE TABLE IF NOT EXISTS oldidlist (
    ID INTEGER NOT NULL        
    )""")
        
        conn.commit()
        self.updatedata()
    
    def updatedata(self):
        c.execute("SELECT nachname FROM personen")
        nachnamenlistealsstring=c.fetchall()
        c.execute("SELECT vorname FROM personen")
        vornamenlistealsstring=c.fetchall()
        c.execute("SELECT geburtsdatum FROM personen")
        geburtsdatenlistealsstring=c.fetchall()
        c.execute("SELECT person_id FROM personen")
        idlistealsstring=c.fetchall()

        nachnamenliste = self.string2list(nachnamenlistealsstring)
        vornamenliste = self.string2list(vornamenlistealsstring)
        geburtsdatenliste = self.string2list(geburtsdatenlistealsstring)
        idliste = self.string2list(idlistealsstring)
        
        self.scrollmatrix = []
        for index,item in enumerate(vornamenliste):
            self.scrollmatrix.append([nachnamenliste[index],item,
                                      geburtsdatenliste[index],idliste[index]])
        
        self.vbox.removeWidget(self.scroll)
        self.scroll.close()
        
        #Hier kommt die Personenanzeige 
        self.scroll = QScrollArea()
        self.personenanzeige = QWidget()
        self.scroll.setWidgetResizable(True)
        
        #Hier kommen die Personen
        
        self.personenanzeigenLayout = QVBoxLayout(self.personenanzeige)
        for person in self.scrollmatrix:
            self.personenanzeigenLayout.addLayout(Row(person))
        self.personenanzeigenLayout.addStretch(1)
        self.personenanzeige.setLayout(self.personenanzeigenLayout)
        self.scroll.setWidget(self.personenanzeige)
        
        self.vbox.addWidget(self.scroll)
        self.vbox.update()
        
    def addPerson(self):
        self.f = addPersonDialog(self)

class Test(QWidget):
    def __init__(self):
        super().__init__()
        self.init()
    def init(self):
        notifyButton1 = QPushButton("Notify1")
        notifyButton1.clicked.connect(self.callnotify)
        notifyButton2 = QPushButton("Notify2")
        notifyButton2.clicked.connect(self.callnotify2)
        closebutton = QPushButton("abstürzen")
        closebutton.clicked.connect(self.crash)
        
        buttonslayout=QVBoxLayout()
        buttonslayout.addWidget(notifyButton1)
        buttonslayout.addWidget(notifyButton2)
        buttonslayout.addWidget(closebutton)
        buttonslayout.addStretch(1)
        self.setLayout(buttonslayout)
    
    def crash(self):
        l=[]
        print(l[1])
    def callnotify(self):
        w.notify(message="Gebetsapp öffnen")
    def callnotify2(self):
        w.notify(ID=w.getrandomid())
    
        
#Hauptklasse       
class App(QTabWidget):
    def __init__(self):
        super().__init__()
        self.init()
    
    def init(self):
        self.tab1= Personenfenster()
        self.tab2= Test()
        
        self.addTab(self.tab1,"Personen")
        self.addTab(self.tab2,"Funktionentest")
        
        #timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.tab2.callnotify2)
        self.timer.start(600000)

        #self.setGeometry(60,25,1305,1010)
        self.setGeometry(60,25,700,1010)
        self.setWindowIcon(QIcon("beten.jpg"))
        self.setWindowTitle("Gebetsapp")
        self.show()

    def notify(self,message=None,ID=None):
        self.notification=Notification(message=message,ID=ID)
        self.notification.setWindowState(w.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.notification.activateWindow()
    
            
    
    def getrandomid(self):
        
        c.execute("""SELECT ID FROM oldidlist""")
        temp = c.fetchall()
        self.oldidlist = []
        for i in temp:
            self.oldidlist.append(i[0])

        c.execute("""SELECT person_id FROM personen""")
        a = c.fetchall()
        idlist=[]
        for i in a:
            idlist.append(i[0])
        workidlist = idlist
        
        if len(workidlist)==0:
            return None
        else:
            for i in workidlist:
                if i in self.oldidlist:
                    workidlist.remove(i)
                    idlist.append(i)
            if len(workidlist) == 0:
                for i in a:
                    workidlist.append(i[0])
                self.oldidlist = []
            random.shuffle(workidlist)
            random.shuffle(workidlist)
            ID = workidlist[0]
            self.oldidlist.append(ID)
            
            #synchronize self.oldidlist with
            c.execute("DROP TABLE IF EXISTS oldidlist")
            c.execute("""CREATE TABLE IF NOT EXISTS oldidlist (ID INTEGER NOT NULL)""")
            for i in self.oldidlist:
                c.execute("""INSERT INTO oldidlist (ID) VALUES ({})""".format(i))
            return ID
    
        
if __name__ == '__main__':
    setup()
    app = QApplication(sys.argv)
    w = App()
    sys.exit(app.exec_())
    conn.close()