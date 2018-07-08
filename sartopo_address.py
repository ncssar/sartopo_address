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
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.firstMarker=True
        self.folderId=None
        self.x=100
        self.y=11
        self.w=300
        self.h=250
        self.addrTable=[["","",""]]
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
    
    def buildTableFromCsv(self,fileName):
        self.addrTable=[["","",""]]
        with open(fileName,'r') as csvFile:
            csvReader=csv.reader(csvFile)
            n=0
            for row in csvReader:
                n=n+1
                self.addrTable.append(row)
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
            self.ui.locationCountLabel.setText(str(n)+" locations loaded")
            self.optionsDialog.ui.locationCountLabel.setText(str(n)+" locations loaded")
            
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
        
    def createFolder(self,folderName):
        infoStr=""
        if self.ui.urlField.text():
            url=self.ui.urlField.text()
            parse=url.lower().replace("http://","").split("/")
            domainAndPort=parse[0]
            mapID=parse[-1]
            print("domainAndPort: "+domainAndPort)
            s=requests.session()
            try:
                s.get(url)
            except:
                QMessageBox.warning(self,"URL Failed","Could not communicate with the specfied URL.  Fix it or blank it out, and try again.")
                infoStr+="\nWrote URL?   NO"
            else:
                folderId=None
                postErr=""
                # first, make a folder to put all the markers in
                f={}
                f['label']="Addresses"
                try:
#                     r=s.post("http://"+domainAndPort+"/rest/folder/",data={'json':json.dumps(f)})
                    r=s.post("http://"+domainAndPort+"/api/v1/map/"+mapID+"/Folder/",data={'json':json.dumps(f)})
                except requests.exceptions.RequestException as err:
                    postErr=err
                else:
                    print("DUMP:")
                    print(json.dumps(f))
                    try:
                        rj=r.json()
                    except:
                        print("ERROR: could not parse json in folder request response.")
                        print("  response text:"+r.content)
                    else:
                        print("RESPONSE:")
                        print(rj)
                        if 'id' in rj:
                            folderId=rj['id']
                        else:
                            print("No folder ID was returned from the folder request;")
                            print("  response content:"+r.content)
        return folderId
 
    def createMarker(self,marker,folderId=None):
        print("createMarker called with folderId="+str(folderId))
        infoStr=""
        if self.firstMarker:
            self.folderId=self.createFolder("Addresses")
            folderId=self.folderId
        if self.ui.urlField.text():
            # the domain and port is defined as the URL up to and including the first slash
            #  after the http:// if it exists, or just the first slash otherwise
            
            # old method (2017, per email 9-29-15):
            #   - first, send a get request to the map URL - this authenticates the session
            #   - next, send a post to domainAndPort/rest/folder/
            
            # new method (May 2018, per email 5-13-18):
            #   - no get request needed
            #   - post to domainAndPort/api/v1/map/<map_id>/Folder/
            
            # in both cases, the folder request json should be "label":"<label>","id":null
        
            # to make sure the map is valid: send a get to domainAndPort/m/<map_id>
            #  it should return 200
            
            # to determine API: try loading domainAndPort/api/v1/map/<map_id>
            #  new API will return 200; old API will return 404
             
            url=self.ui.urlField.text()
            parse=url.lower().replace("http://","").split("/")
            domainAndPort=parse[0]
            mapID=parse[-1]
            print("domainAndPort: "+domainAndPort)
            s=requests.session()
            try:
                s.get(url)
            except:
                QMessageBox.warning(self,"URL Failed","Could not communicate with the specfied URL.  Fix it or blank it out, and try again.")
                infoStr+="\nWrote URL?   NO"
            else:
                postErr=""
                j={}
                j['label']=marker[0]
                j['folderId']=folderId
                j['url']=""
                j['comments']=""
                j['position']={"lat":marker[1],"lng":marker[2]}
                try:
#                             r=s.post("http://"+domainAndPort+"/rest/marker/",data={'json':json.dumps(j)})
                     r=s.post("http://"+domainAndPort+"/api/v1/map/"+mapID+"/Marker/",data={'json':json.dumps(j)})
                except requests.exceptions.RequestException as err:
                    postErr=err
                else:
                    print("DUMP:")
                    print(json.dumps(j))
                if postErr=="":
                    infoStr+="\nWrote URL?   YES"
                    self.firstMarker=False
                else:
                    infoStr+="\nWrote URL?   NO"
                    QMessageBox.warning(self,"URL Post Request Failed","URL POST request failed:\n\n"+str(postErr)+"\n\nNo markers written to URL.  Fix or blank out the URL field, and try again.")
    
    def go(self):
        self.createMarker([" ".join(self.ui.addrField.text().split()[0:2]),self.ui.latField.text(),self.ui.lonField.text()],self.folderId)

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