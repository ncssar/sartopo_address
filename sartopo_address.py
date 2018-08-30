# #############################################################################
#
#  sartopo_address.py - add a marker to sartopo for a specified street address,
#    street name, or intersection; designed for use while offline, using
#    a database of addresses and their corresponding lat/lon coordinates
#
#   developed for Nevada County Sheriff's Search and Rescue
#    Copyright (c) 2018 Tom Grundy
#
#  http://github.com/ncssar/sartopo_address
#
#  Contact the author at nccaves@yahoo.com
#   Attribution, feedback, bug reports and feature requests are appreciated
#
#  REVISION HISTORY
#-----------------------------------------------------------------------------
#   DATE   |  AUTHOR  |  NOTES
#-----------------------------------------------------------------------------
#  7-4-18    TMG        First version
#  7-4-18    TMG        fix #11 (resource file to remember location file name)
#  7-4-18    TMG        fix #12 (handle missing .rc file)
#  7-8-18    TMG        first pass at adding street names (all with 39 -120)
#  7-8-18    TMG        interim solution for street name coordinates: use
#                        the coordinates of the first address encountered
#                        on that street; hopefully soon to be replaced by
#                        a method that draws the entire line for that street;
#                        set the street marker label to use all words of the
#                        street name up to but excluding the street suffix
#                        (this rule works for exact addresses and for streets);
#                        hardcode to always stay on top
# 7-13-18     TMG       fix #13 (marker labels cannot be changed later)
# 8-29-18     TMG       fix #1 (autodetect sartopo API version / use a module)
#
# #############################################################################
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  See included file LICENSE.txt for full license terms, also
#  available at http://opensource.org/licenses/gpl-3.0.html
#
# ############################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys
import csv
import requests
import json
import re

from sartopo_python import SartopoSession

from sartopo_address_ui import Ui_Dialog
from options_dialog_ui import Ui_optionsDialog

class MyWindow(QDialog,Ui_Dialog):
    def __init__(self,parent):
        QDialog.__init__(self)
        self.parent=parent
        self.rcFileName="sartopo_address.rc"
        self.ui=Ui_Dialog()
        self.ui.setupUi(self)
        self.locationFile="sartopo_address.csv"
        self.optionsDialog=optionsDialog(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.firstMarker=True
        self.folderId=None
        self.sts=None
        self.x=100
        self.y=11
        self.w=300
        self.h=250
        self.addrTable=[["","",""]]
        self.streetAndCityTable=[["","",""]]
#         self.addrTable=[["301 Redbud Way",39,-120],
#                         ["322 Sacramento Street",38,-121],
#                         ["123 Joe Place",32,-122],
#                         ["1262 Redbud Lane",37,-123]]
        

        self.loadRcFile()
        self.setGeometry(int(self.x),int(self.y),int(self.w),int(self.h))
        self.buildTableFromCsv(self.locationFile)
#         self.ui.locationCountLabel.setText(str(len(self.addrTable))+" locations loaded")
        
        self.addrTableModel=MyTableModel(self.addrTable,self)
        
        # using a simple string list is easier than an AbstractTableModel subclass
        self.completer=QCompleter([x[0] for x in self.addrTable])
#         self.completer=QCompleter()
#         self.completer.setModel(self.addrTableModel)

        # performance speedups: see https://stackoverflow.com/questions/33447843
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setModelSorting(QCompleter.CaseSensitivelySortedModel)
        self.completer.popup().setUniformItemSizes(True)
        self.completer.popup().setLayoutMode(QListView.Batched)
        
        self.ui.addrField.setCompleter(self.completer)
        self.ui.addrField.textChanged.connect(self.lookupFromAddrField)
        self.ui.optionsButton.clicked.connect(self.optionsDialog.show)
        
#         box=QLabel("BOX",self.ui.optionsButton)
#         box.setStyleSheet("background:blue;border:2px outset green")
#         box.setGeometry(-10,-10,25,25)
        self.ui.optionsButton.setToolTip("stuff")
#         self.ui.optionsButton.showText([100,100],"stuff1")
#         tt1=QToolTip(self.ui)
#         tt2=QToolTip(self.ui)

#         self.getUrl()
    
    def buildTableFromCsv(self,fileName):
        self.addrTable=[["","",""]]
        self.scLowestDict={}
        with open(fileName,'r') as csvFile:
            csvReader=csv.reader(csvFile)
            n=0
            for row in csvReader:
                n=n+1
                self.addrTable.append(row)
            # also add each street-and-city (just once) as its own entry;
            #  for coordinates (for now), use a fixed offset from the
            #  coordinates of the lowest number on that street
            for row in self.addrTable:
#                 print("row:"+str(row))
                addrParse=row[0].split()
#                 print("parse:"+str(addrParse))
                if len(addrParse)>0:
                    number=addrParse[0]
                    streetAndCity=' '.join(addrParse[1:])
    #                 streetAndCity=re.sub(r'^[0-9]+ ','',row[0])
    #                 scRow=[streetAndCity,row[1],row[2]]
    #                 scnRow=[streetAndCity,number,row[1],row[2]]
#                     if streetAndCity=="Whispering Pines Lane, Grass Valley":
#                         print("street found: number="+str(number)+"  "+str(row))
#                         print("   existing dict entry="+str(self.scLowestDict.get(streetAndCity,'none')))
#                     if (not streetAndCity in self.scLowestDict) or (number<self.scLowestDict[streetAndCity][0]):
                    if not streetAndCity in self.scLowestDict:
                        self.scLowestDict[streetAndCity]=[number,row[1],row[2]]
#                         if streetAndCity=="Whispering Pines Lane, Grass Valley":
#                             print("lowest number so far for street: "+str(number)+" "+streetAndCity)
    #                     self.scnTable.append(scnRow)
#                 else: # it does exist; but if the current number is lower,
                    # replace the existing entry with the current entry
#                     print("adding street: "+streetAndCity)
#                     if number<self.scLowestDict[streetAndCity]:
#                         self.scnTable
#             self.addrTable=self.addrTable+self.streetAndCityTable
            for key,value in self.scLowestDict.items():
                row=[key,value[1],value[2]]
                self.addrTable.append(row)
#                 print("adding "+str(row))
            # performance speedup: sort alphabetically on the column that 
            #  will be used for lookup; see setModelSorting docs
            self.addrTable.sort(key=lambda x: x[0])
            self.completer=QCompleter([x[0] for x in self.addrTable])
            # performance speedups: see https://stackoverflow.com/questions/33447843
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.completer.setModelSorting(QCompleter.CaseSensitivelySortedModel)
            self.completer.popup().setUniformItemSizes(True)
            self.completer.popup().setLayoutMode(QListView.Batched)
            
            self.ui.addrField.setCompleter(self.completer)
            print("Finished reading "+str(n)+" addresses.")
            print("Added "+str(len(self.scLowestDict))+" street names.")
            self.ui.locationCountLabel.setText(str(n)+" locations loaded")
            self.optionsDialog.ui.locationCountLabel.setText(str(n)+" locations loaded")

    def createSTS(self):
        if self.ui.urlField.text():
            url=self.ui.urlField.text()
            parse=url.lower().replace("http://","").split("/")
            domainAndPort=parse[0]
            mapID=parse[-1]
            self.sts=SartopoSession(mapID)
            
#     def getUrl(self):
#         stateFile="C:\Users\caver\AppData\Local\Google\Chrome\User Data\Local State"
#         with open(stateFile,'r') as s:
#             j=json.loads(s.read())
#             s.close()     
#         
#         chrome_window=Desktop(backend="uia").window(class_name_re='Chrome')
#         address_bar_wrapper=chrome_window['Google Chrome'].main.Edit.wrapper_object()
#         url_1=address_bar_wrapper.legacy_properties()['Value']
#         url_2=address_bar_wrapper.iface_value.CurrentValue
#         print("url 1:'"+url_1+"'")
#         print("url 2:'"+url_2+"'")
    
    def lookupFromAddrField(self):
        addr=self.ui.addrField.text().lower()
#         # reduce lag by skipping lookup until more than 3 characters
#         #  have been entered
#         if len(addr)<4:
#             return
        for row in self.addrTable:
            if row[0].lower()==addr:
                self.ui.latField.setText(str(row[1]))
                self.ui.lonField.setText(str(row[2]))
                return
        self.ui.latField.setText("")
        self.ui.lonField.setText("")  

    def saveRcFile(self):
        print("saving...")
        (x,y,w,h)=self.geometry().getRect()
        rcFile=QFile(self.rcFileName)
        if not rcFile.open(QFile.WriteOnly|QFile.Text):
            warn=QMessageBox(QMessageBox.Warning,"Error","Cannot write resource file " + self.rcFileName + "; proceeding, but, current settings will be lost. "+rcFile.errorString(),
                            QMessageBox.Ok,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
            warn.show()
            warn.raise_()
            warn.exec_()
            return
        out=QTextStream(rcFile)
        out << "[sartopo_address]\n"
        out << "locationFile=" << self.locationFile << "\n"
        out << "x=" << x << "\n"
        out << "y=" << y << "\n"
        out << "w=" << w << "\n"
        out << "h=" << h << "\n"
        rcFile.close()
        
    def loadRcFile(self):
        print("loading...")
        rcFile=QFile(self.rcFileName)
        if not rcFile.open(QFile.ReadOnly|QFile.Text):
            warn=QMessageBox(QMessageBox.Warning,"Error","Cannot read resource file " + self.rcFileName + "; using default settings. "+rcFile.errorString(),
                            QMessageBox.Ok,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
            warn.show()
            warn.raise_()
            warn.exec_()
            return
        inStr=QTextStream(rcFile)
        line=inStr.readLine()
        if line!="[sartopo_address]":
            warn=QMessageBox(QMessageBox.Warning,"Error","Specified resource file " + self.rcFileName + " is not a valid resource file; using default settings.",
                            QMessageBox.Ok,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
            warn.show()
            warn.raise_()
            warn.exec_()
            rcFile.close()
            return
        while not inStr.atEnd():
            line=inStr.readLine()
            tokens=line.split("=")
            if tokens[0]=="x":
                self.x=int(tokens[1])
            elif tokens[0]=="y":
                self.y=int(tokens[1])
            elif tokens[0]=="w":
                self.w=int(tokens[1])
            elif tokens[0]=="h":
                self.h=int(tokens[1])
            elif tokens[0]=="locationFile":
                self.locationFile=tokens[1]
            elif tokens[0]=="font-size":
                self.fontSize=int(tokens[1].replace('pt',''))
        rcFile.close()
    
    def getStreetLabel(self):
        addr=self.ui.addrField.text()
        parse=addr.split()
        # assume that the street suffix token ends with a comma
        n=0
        for n in range(len(parse)):
            print("testing "+parse[n])
            if parse[n][len(parse[n])-1]==",":
                break
        if n==0:
            n=2
        return ' '.join(parse[0:n])
    
    def go(self):
        if self.firstMarker:
            self.folderId=self.sts.addFolder("Addresses")
            self.firstMarker=False
        self.sts.addMarker(self.ui.latField.text(),self.ui.lonField.text(),self.getStreetLabel(),self.folderId)

    def closeEvent(self,event):
        self.saveRcFile()
        event.accept()
        self.parent.quit()

class optionsDialog(QDialog,Ui_optionsDialog):
    def __init__(self,parent):
        QDialog.__init__(self)
        self.parent=parent
        self.ui=Ui_optionsDialog()
        self.ui.setupUi(self)
        self.ui.locationFileField.setText(self.parent.locationFile)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags((self.windowFlags() | Qt.WindowStaysOnTopHint) & ~Qt.WindowMinMaxButtonsHint & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(self.size())

    def showEvent(self,event):
        # clear focus from all fields, otherwise previously edited field gets focus on next show,
        # which could lead to accidental editing
        self.ui.locationFileField.clearFocus()
        self.ui.locationFileField.setText(self.parent.locationFile)
        
    def displayLocationCount(self):
        self.ui.locationCountLabel.setText(str(len(self.parent.addrTable))+" locations loaded")
        self.parent.ui.locationCountLabel.setText(str(len(self.parent.addrTable))+" locations loaded")
    
    def browseForFile(self):
        fileDialog=QFileDialog()
        fileDialog.setOption(QFileDialog.DontUseNativeDialog)
        fileDialog.setWindowFlags(Qt.WindowStaysOnTopHint)
#         fileDialog.setProxyModel(CSVFileSortFilterProxyModel(self))
        fileDialog.setNameFilter("CSV Location Lookup Files (*.csv)")
#         fileDialog.setDirectory(self.firstWorkingDir)
        if fileDialog.exec_():
            fileName=fileDialog.selectedFiles()[0]
            self.ui.locationFileField.setText(fileName)
            self.parent.locationFile=fileName
        else: # user pressed cancel on the file browser dialog
            return
        
    def reload(self):
#         self.parent.addrTable=[[]]
        self.parent.buildTableFromCsv(self.ui.locationFileField.text())
        self.displayLocationCount()
        
        
class MyTableModel(QAbstractTableModel):
    def __init__(self, datain, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata=datain

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.EditRole:
            return QVariant()
        try:
            rval=QVariant(self.arraydata[index.row()][index.column()])
        except:
            row=index.row()
            col=index.column()
            rprint("Row="+str(row)+" Col="+str(col))
            rprint("arraydata:")
            rprint(self.arraydata)
        else:
            return rval
        
        
def main():
    app = QApplication(sys.argv)
    w = MyWindow(app)
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()