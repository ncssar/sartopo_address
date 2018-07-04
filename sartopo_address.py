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

class MyWindow(QDialog,Ui_Dialog):
    def __init__(self,parent):
        QDialog.__init__(self)
        self.parent=parent
        self.rcFileName="sartopo_address.rc"
        self.ui=Ui_Dialog()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.firstMarker=True
        self.folderId=None
        
        self.addrTable=[[]]
        self.addrTable=[["301 Redbud Way",39,-120],
                        ["322 Sacramento Street",38,-121],
                        ["123 Joe Place",32,-122],
                        ["1262 Redbud Lane",37,-123]]
        
        self.buildTableFromCsv("C:\\Users\\caver\\Downloads\\nevadacountyaddresses.csv")
        
        self.addrTableModel=MyTableModel(self.addrTable,self)
        
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
    
    def buildTableFromCsv(self,fileName):
        with open(fileName,'r') as csvFile:
            csvReader=csv.reader(csvFile)
            n=0
            for row in csvReader:
                n=n+1
                self.addrTable.append(row)
            self.addrTable.sort(key=lambda x: x[0])
            print("Finished reading "+str(n)+" addresses.")
            
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
        self.ui.latField.setText("---")
        self.ui.lonField.setText("---")  
                
#         i=self.addrTableModel.match(self.addrTableModel.createIndex(0,0),Qt.EditRole,addr)[0]
#         r=self.addrTableModel.data(i,Qt.EditRole)
#         print("data="+str(r)+"  type="+str(r.type()))
#         lat=r[1]
#         lon=r[2]
#         self.ui.latField.setText(str(lat))
#         self.ui.lonField.setText(str(lon))

    def createFolder(self,folderName):
        infoStr=""
        if self.ui.urlField.text():
            url=self.ui.urlField.text()
            parse=url.lower().replace("http://","").split("/")
            domainAndPort=parse[0]
            mapCode=parse[-1]
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
                    r=s.post("http://"+domainAndPort+"/api/v1/map/"+mapCode+"/Folder/",data={'json':json.dumps(f)})
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
            
            url=self.ui.urlField.text()
            parse=url.lower().replace("http://","").split("/")
            domainAndPort=parse[0]
            mapCode=parse[-1]
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
                     r=s.post("http://"+domainAndPort+"/api/v1/map/"+mapCode+"/Marker/",data={'json':json.dumps(j)})
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