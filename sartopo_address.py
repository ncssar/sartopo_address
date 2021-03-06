# #############################################################################
#
#  sartopo_address.py - add a marker to sartopo for a specified street address,
#    street name, or intersection; designed for use while offline, using
#    a database of addresses and their corresponding lat/lon coordinates
#
#   developed for Nevada County Sheriff's Search and Rescue
#    Copyright (c) 2020 Tom Grundy
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
#  10-7-18    TMG       modify to work with api upgrades in sartopo_python
#                         (probably not backwards compatible); incorporate USAR
#                         symbol selection
# 7-3-19      TMG       allow edit of an existing marker; filter list of existing
#                         markers based on selected folder name; use custom combo box
#                         to allow update of folders and filtered markers when the
#                         combo box is selected; add link status indicator lights
#                         to show if a valid API and mapID has been connected;
#                         enforce min required version of sartopo_python
#  3-30-20    TMG       fix #23: preserve folder and symbol when editing an existing marker;
#                         fix #19: add 'Go' button to reduce chance for accidental marker moves;
#                         add optional timestamp that populates the 'description' field;
#                         required sartopo_python_min_version increased to 1.0.6
#                         because entire property set must be returned with each marker
#   6-9-20    TMG       fix #24: sartopo.com signed requests (requires sartopo_python 1.1.2);
#                         fix #25: window opens outside of display boundary
#   8-24-20   TMG       fix #29: esc should not close main window
#   8-28-20   TMG       fix #26 fix #27 fix #28 fix #31; overhaul to allow custom markers
#                         with preset folder names
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

import os
import sys
import csv
import json
import re
import time
from datetime import datetime

sartopo_python_min_version="1.1.2"

import pkg_resources
sartopo_python_installed_version=pkg_resources.get_distribution("sartopo-python").version
print("sartopo_python version:"+str(sartopo_python_installed_version))
if pkg_resources.parse_version(sartopo_python_installed_version)<pkg_resources.parse_version(sartopo_python_min_version):
	print("ABORTING: installed sartopo_python version "+str(sartopo_python_installed_version)+" is less than minimum required version "+sartopo_python_min_version)
	exit()
	
from sartopo_python import SartopoSession

from sartopo_address_ui import Ui_Dialog
from options_dialog_ui import Ui_optionsDialog

markerSymbolDict={}
markerSymbolDict["Animal Issue"]="usar-14"
markerSymbolDict["IC"]="cp"
markerSymbolDict["Warning"]="warning"
markerSymbolDict["Structure No Damage"]="usar-1"
markerSymbolDict["Structure Damaged"]="usar-2"
markerSymbolDict["Structure Failed"]="usar-3"
markerSymbolDict["Structure Destroyed"]="usar-4"
markerSymbolDict["No Damage"]="usar-1"
markerSymbolDict["Damaged"]="usar-2"
markerSymbolDict["Failed"]="usar-3"
markerSymbolDict["Destroyed"]="usar-4"
markerSymbolDict["Assisted"]="usar-5"
markerSymbolDict["Evacuated"]="usar-6"
markerSymbolDict["Rescued"]="usar-7"
markerSymbolDict["Follow-Up"]="usar-8"
markerSymbolDict["Follow-up"]="usar-8"
markerSymbolDict["Follow Up"]="usar-8"
markerSymbolDict["Follow up"]="usar-8"
markerSymbolDict["Shelter In Place"]="usar-13"
markerSymbolDict["Route Blocked"]="usar-20"

def sortByTitle(item):
	return item["properties"]["title"]

class MyWindow(QDialog,Ui_Dialog):
	def __init__(self,parent):
		QDialog.__init__(self)
		self.parent=parent
		self.rcFileName="sartopo_address.rc"
		self.ui=Ui_Dialog()
		self.ui.setupUi(self)
		self.locationFileName="sartopo_address.csv"
		self.markerFileName="sartopo_markers.csv"
		self.accountName=""
		self.previousComment=""
		self.optionsDialog=optionsDialog(self)
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.url=None
		self.folderId=None
		self.sts=None
		self.link=-1
		self.x=100
		self.y=11
		self.w=300
		self.h=250
		self.lat=None
		self.lon=None
		self.addrTable=[["","",""]]
		self.streetAndCityTable=[["","",""]]
		self.sinceFolder=0 # sartopo wants integer milliseconds
		self.sinceMarker=0 # sartopo wants integer milliseconds
		self.markerList=[] # list of all sartopo markers and their ids

		self.ui.existingMarkerComboBox.featureClass="Marker"
		self.ui.existingMarkerComboBox.headerText="Existing Marker"
		
		self.ui.folderComboBox.featureClass="Folder"
		# self.ui.folderComboBox.headerText="Folder"

		self.loadRcFile()
		self.loadMarkerFile()

		self.setGeometry(int(self.x),int(self.y),int(self.w),int(self.h))
		self.buildTableFromCsv(self.locationFileName)
		
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

		self.featureListWidgetsToUpdate={}
		self.featureListWidgetsToUpdate["Folder"]=[self.ui.folderComboBox,self.optionsDialog.ui.folderComboBox]
		self.featureListWidgetsToUpdate["Marker"]=[self.ui.existingMarkerComboBox]
		
		self.since={}
		self.since["Folder"]=0
		self.since["Marker"]=0
		
		self.featureListDict={}
		self.featureListDict["Folder"]=[]
		self.featureListDict["Marker"]=[]
	
		self.modeChanged()
		self.ui.goButton.setEnabled(False) # only enable the button when ready
		
		# use the filter folder combo box selection to filter the edit marker combo box items
		self.ui.existingMarkerComboBox.filterFolderComboBox=self.optionsDialog.ui.folderComboBox
		
		QTimer.singleShot(500,lambda:self.optionsDialog.show())

	# prevent 'esc' from closing the newEntryWindow - copied from radiolog
	def keyPressEvent(self,event):
		if event.key()!=Qt.Key_Escape:
			QDialog.keyPressEvent(self,event)
	
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

	def updateLinkIndicator(self):
		if self.link==1:
			self.ui.linkIndicator.setStyleSheet("background-color:#00ff00")
			self.optionsDialog.ui.linkIndicator.setStyleSheet("background-color:#00ff00")
		else:
			self.ui.linkIndicator.setStyleSheet("background-color:#ff0000")
			self.optionsDialog.ui.linkIndicator.setStyleSheet("background-color:#ff0000")

	def createSTS(self):
		print("\ncreateSTS called:")
		if self.sts is not None: # close out any previous session
			print("Closing previous SartopoSession")
			self.sts=None
			self.ui.linkIndicator.setText("")
			self.updateLinkIndicator()
			self.link=-1
			self.updateFeatureList("Folder")
			self.updateFeatureList("Marker")
		if self.optionsDialog.ui.urlField.text():
			u=self.optionsDialog.ui.urlField.text()
			if u==self.url: # url has not changed; keep the existing link and folder list
				return
			self.url=u
			if self.url.endswith("#"): # pound sign at end of URL causes crash; brute force fix it here
				self.url=self.url[:-1]
				self.optionsDialog.ui.urlField.setText(self.url)
			parse=self.url.replace("http://","").replace("https://","").split("/")
			domainAndPort=parse[0]
			mapID=parse[-1]
			print("calling SartopoSession with domainAndPort="+domainAndPort+" mapID="+mapID)
			if 'sartopo.com' in domainAndPort.lower():
				print("  creating online session for user "+self.accountName)
				self.sts=SartopoSession(domainAndPort=domainAndPort,mapID=mapID,
										configpath="../sts.ini",
										account=self.accountName)
			else:
				self.sts=SartopoSession(domainAndPort=domainAndPort,mapID=mapID)
			self.link=self.sts.apiVersion
			print("link status:"+str(self.link))
			self.updateLinkIndicator()
			if self.link>0:
				self.ui.linkIndicator.setText(self.sts.mapID)
				self.updateFeatureList("Folder")
			self.optionsDialog.ui.folderComboBox.setHeader("Select a Folder...")
			
	# def folderComboBoxActivated(self):
	# 	self.featureListWidgetToUpdate["Folder"]=self.ui.folderComboBox
	# 	self.updateFeatureList("Folder")
	# 	self.featureListWidgetToUpdate["Folder"]=self.optionsDialog.ui.folderComboBox

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
				self.lat=row[1]
				self.lon=row[2]
				self.ui.latLonField.setText(str(self.lat)+" "+str(self.lon))
				# self.ui.latLonField.setText(str(row[1]+" "+str(row[2])))
				self.goButtonSetEnabled()
				self.ui.existingMarkerComboBox.setEnabled(True)
				self.updateTimestamp()
				return
		self.lat=None
		self.lon=None
		self.ui.latLonField.setText("")
		self.goButtonSetEnabled()
		self.ui.existingMarkerComboBox.setEnabled(False)

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
		out << "locationFileName=" << self.locationFileName << "\n"
		out << "markerFileName=" << self.markerFileName << "\n"
		out << "accountName=" << self.accountName << "\n"
		out << "x=" << x << "\n"
		out << "y=" << y << "\n"
		out << "w=" << w << "\n"
		out << "h=" << h << "\n"
		rcFile.close()

	def loadMarkerFile(self):
		print("loading marker file...")
		markerFile=QFile(self.markerFileName)
		if not markerFile.open(QFile.ReadOnly|QFile.Text):
			warn=QMessageBox(QMessageBox.Warning,"Error","Cannot read marker file " + self.markerFileName + "; using default marker settings. "+markerFile.errorString(),
							QMessageBox.Ok,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
			warn.show()
			warn.raise_()
			warn.exec_()
			return
		inStr=QTextStream(markerFile)
		line=inStr.readLine()
		if "# SARTopo Address Tool marker definitions" not in line:
			warn=QMessageBox(QMessageBox.Warning,"Error","Specified marker file " + self.markerFileName + " is not a valid marker definition file; using default marker settings.",
							QMessageBox.Ok,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
			warn.show()
			warn.raise_()
			warn.exec_()
			markerFile.close()
			return
		markerFile.close()
		with open(self.markerFileName,'r') as markerFile:
			self.markerList=[] # use list instead of dict to keep sequence from file
			csvReader=csv.reader(markerFile)
			for row in csvReader:
				if not row[0].startswith("#"):
					self.markerList.append(row)
			self.buildMarkerSymbolComboBox()

	def buildMarkerSymbolComboBox(self):
		self.ui.markerSymbolComboBox.clear()
		for marker in self.markerList:
			self.ui.markerSymbolComboBox.addItem(
					QIcon(":/sartopo_address/sartopo_markers/"+marker[1]),marker[0],marker[2:])

	def markerSymbolComboBoxCB(self):
		data=self.ui.markerSymbolComboBox.currentData()
		print("\nmarkerSymbolComboBoxCB called:\n  folderComboBox items:"+str(self.ui.folderComboBox.getItems())+"\n  currentData:"+str(data))
		if data is not None and isinstance(data,list):
			self.markerSymbol=data[0]
			self.markerFolder=data[1]
			# if not already in the folder list, add it as an entry; making editable and setting
			#  the edit text has less desirable behavior: if you click the combo box pulldown, the
			#  edit text is gone.  If unused, that's OK, because the folder combo box refreshes
			#  itself from the actual list of folders on the map for each new marker anyway.
			# if self.markerFolder not in [self.ui.folderComboBox.itemText(i) for i in range(self.ui.folderComboBox.count())]:
			# 	self.ui.folderComboBox.addItem(self.markerFolder)
			# 	self.ui.folderComboBox.extraItems=[self.markerFolder] # so that it remains after refresh
			# self.ui.folderComboBox.setCurrentText(self.markerFolder)
			self.ui.folderComboBox.headerText=self.markerFolder
			self.ui.folderComboBox.setHeader(self.markerFolder)
			self.ui.folderComboBox.setCurrentIndex(0)

	def loadRcFile(self):
		print("loading rc file "+self.rcFileName+"...")
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
			elif tokens[0]=="locationFileName":
				self.locationFileName=tokens[1]
			elif tokens[0]=="markerFileName":
				self.markerFileName=tokens[1]
			elif tokens[0]=="accountName":
				self.accountName=tokens[1]
			elif tokens[0]=="font-size":
				self.fontSize=int(tokens[1].replace('pt',''))
		d=QApplication.desktop()
		if self.x > d.availableGeometry(self).width():
			self.x=300
		if self.y > d.availableGeometry(self).height():
			self.y=300
		rcFile.close()
	
	def getStreetLabel(self):
		addr=self.ui.addrField.text()
		parse=addr.split()
		# assume that the street suffix token ends with a comma
		n=0
		for n in range(len(parse)):
			# print("testing "+parse[n])
			if parse[n][len(parse[n])-1]==",":
				break
		if n==0:
			n=2
		return ' '.join(parse[0:n])
	
	# def getMarkerSymbol(self):
	# 	t=self.ui.markerSymbolComboBox.currentText()
	# 	symbol=markerSymbolDict.get(t,"point")
	# 	return symbol

	def getDescription(self):
		d=re.sub(" \[\d\d\d\d\.\d\d\d\d]","",self.ui.commentField.text())
		if self.ui.timestampCheckbox.isChecked():
			if d!="":
				d+=" "
			d+="["+self.ui.timestampField.text()+"]"
		if d=="":
			return None
		else:
			return d

	def addMarker(self):
#         if self.firstMarker:
#             self.folderId=self.sts.addFolder("Addresses")
#             self.firstMarker=False
		folders=self.sts.getFeatures("Folder")
		fid=False
		folderName=self.ui.folderComboBox.currentText()
		if folderName=="Folder":
			folderName="Addresses"
		for folder in folders:
			if folder["properties"]["title"]==folderName:
				fid=folder["id"]
		# make a folder by the selected name if it doesn't already exist
		if not fid:
			fid=self.sts.addFolder(folderName)
		self.folderId=fid
		# rval=self.sts.addMarker(self.ui.latField.text(),self.ui.lonField.text(),self.getStreetLabel(),self.getDescription(),"FF0000",self.getMarkerSymbol(),None,self.folderId)
		rval=self.sts.addMarker(self.lat,self.lon,self.getStreetLabel(),self.getDescription(),"FF0000",self.markerSymbol,None,self.folderId)
		print("addMarker response:"+str(rval))
	
	def updateFeatureList(self,featureClass,filterFolderId=None):
		# unfiltered feature list should be kept as an object;
		#  filtered feature list (i.e. combobox items) should be recalculated here on each call 
		print("updateFeatureList called: "+featureClass+"  filterFolderId="+str(filterFolderId))
		if self.sts and self.link>0:
			rval=self.sts.getFeatures(featureClass,self.since[featureClass])
			self.since[featureClass]=int(time.time()*1000) # sartopo wants integer milliseconds
			
			# update and sort the unfiltered list only if there are new features in rval;
			#  note that old features may be returned from the API if their attributes have changed
			#  (name, symbol, folder id, etc etc);
			#  we want to make sure the unfiltered list always has the latest, so, if
			#  a new version of an old object was returned by the API, first remove the old
			#  version from the unfiltered list, then add the new version
			if rval:
				print("rval:"+str(rval))
				for feature in rval:
					# if there's a previous version of the same feature (based on ID only),
					#  remove the previous version from the list
					for oldFeature in self.featureListDict[featureClass]:
						if feature["id"]==oldFeature["id"]:
							self.featureListDict[featureClass].remove(oldFeature)
					self.featureListDict[featureClass].append(feature)
				self.featureListDict[featureClass].sort(key=sortByTitle)
				
			# recreate the filtered list regardless of whether there were new features in rval    
			items=[]
			for feature in self.featureListDict[featureClass]:
				id=feature.get("id",0)
				prop=feature.get("properties",{})
				name=prop.get("title","UNNAMED")
				add=True
				if filterFolderId:
					fid=prop.get("folderId",0)
					if fid!=filterFolderId:
						add=False
						print("      filtering out feature:"+str(id))
				if add:
					print("    adding feature:"+str(id))
					if featureClass=="Folder":
						items.append([name,id])
					else:
						items.append([name,[id,prop]])
			else:
				print("no return data, i.e. no new features of this class since the last check")
		else:
			print("No map link has been established yet.  Could not get Folder objects.")
			self.featureListDict[featureClass]=[]
			self.since[featureClass]=0
			items=[]
		print("  unfiltered list:"+str(self.featureListDict[featureClass]))
		print("  filtered list:"+str(items))
		
		# add custom default folder at start of list if needed
		
		# update the specified combo box's items
		for w in self.featureListWidgetsToUpdate[featureClass]:
			print("updating "+str(w.objectName()))
			w.setItems(items)
		
	def editMarker(self):
		name=self.ui.existingMarkerComboBox.currentText()
		data=self.ui.existingMarkerComboBox.currentData()
		id=data[0]
		prop=data[1]
		print("editMarker called: selection="+name+"  id="+id)
		# now set current index to -1 so that subsequent focus action will trigger
		#  populateComboBox again (from the highlighted slot)
		fid=prop.get("folderId",None)
		symbol=prop.get("marker-symbol","point")
		self.sts.addMarker(self.lat,self.lon,name,description=self.getDescription(),symbol=symbol,folderId=fid,existingId=id)
		self.ui.existingMarkerComboBox.setCurrentIndex(0)
		
	def closeEvent(self,event):
		self.saveRcFile()
		event.accept()
		self.parent.quit()
		
	def modeChanged(self):
		self.mode=self.ui.modeComboBox.currentText()
		print("mode changed to '"+self.mode+"'")
		if self.mode=="Add":
			showAddFields=True
			showMoveFields=False
			self.markerSymbolComboBoxCB()
		elif self.mode=="Move":
			showAddFields=False
			showMoveFields=True
			self.ui.existingMarkerComboBox.setCurrentIndex(0) # to trigger the callback
			self.updateTimestamp()
		else:
			showAddFields=False
			showMoveFields=False
		self.ui.markerSymbolComboBox.setEnabled(showAddFields)
		self.ui.markerSymbolComboBox.setVisible(showAddFields)
		self.ui.folderComboBox.setVisible(showAddFields)
		self.ui.folderLabel.setVisible(showAddFields)
		self.ui.existingMarkerComboBox.setEnabled(showMoveFields)
		self.ui.existingMarkerComboBox.setVisible(showMoveFields)
		# self.ui.timestampLabel.setVisible(showMoveFields)
		# self.ui.timestampCheckbox.setVisible(showMoveFields)
		# self.ui.timestampField.setEnabled(self.ui.timestampCheckbox.isChecked())
		# self.ui.timestampField.setVisible(showMoveFields)
		self.ui.commentField.setText("")
		self.goButtonSetEnabled()

	def clearAddress(self):
		self.ui.addrField.setText("")
		self.ui.latLonField.setText("")
		self.goButtonSetEnabled()
	
	def updateTimestamp(self):
		self.ui.timestampField.setText(datetime.now().strftime("%m%d.%H%M"))

	def existingMarkerComboBoxCB(self):
		self.updateTimestamp()
		self.goButtonSetEnabled()
		box=self.ui.existingMarkerComboBox
		data=box.currentData()
		self.ui.commentField.setText("")
		print("Existing marker selected:"+str(box.currentText()))		
		if data is not None:
			try:
				print("  data:"+str(box.currentData()))
				print("    json:"+str(box.currentData()[1]))
				self.previousComment=box.currentData()[1]["description"]
				print("  comment:"+str(self.previousComment))
				self.updateComment()
			except:
				pass

	def updateComment(self):
		if self.mode=="Move":
			self.ui.commentField.setText(self.previousComment)
			if self.ui.timestampCheckbox.isChecked():
				self.ui.commentField.setText(re.sub("\[\d\d\d\d\.\d\d\d\d]","["+self.ui.timestampField.text()+"]",self.previousComment))

	def timestampCheckboxCB(self):
		self.ui.timestampField.setEnabled(self.ui.timestampCheckbox.isChecked())
		self.updateComment()
	
	def goButtonSetEnabled(self):
		if self.mode=="Add" and self.lat!=None:
			self.ui.goButton.setEnabled(True)
		elif self.mode=="Move" and (self.lat!=None and self.ui.existingMarkerComboBox.currentText()!="Existing Marker"):
			self.ui.goButton.setEnabled(True)
		else:
			self.ui.goButton.setEnabled(False)
   
	def go(self):
		if self.mode=="Add":
			self.addMarker()
		elif self.mode=="Move":
			self.editMarker()
				

class optionsDialog(QDialog,Ui_optionsDialog):
	def __init__(self,parent):
		QDialog.__init__(self)
		self.parent=parent
		self.ui=Ui_optionsDialog()
		self.ui.setupUi(self)
		self.ui.locationFileField.setText(self.parent.locationFileName)
		self.ui.markerFileField.setText(self.parent.markerFileName)
		self.ui.accountNameField.setText(self.parent.accountName)
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		self.setWindowFlags((self.windowFlags() | Qt.WindowStaysOnTopHint) & ~Qt.WindowMinMaxButtonsHint & ~Qt.WindowContextHelpButtonHint)
		self.setFixedSize(self.size())
		self.ui.folderComboBox.featureClass="Folder"
		self.ui.folderComboBox.headerText="Select a Folder..."
		self.ui.folderComboBox.setItems([])

	def showEvent(self,event):
		# clear focus from all fields, otherwise previously edited field gets focus on next show,
		# which could lead to accidental editing
		self.ui.locationFileField.clearFocus()
		self.ui.locationFileField.setText(self.parent.locationFileName)
		self.ui.markerFileField.clearFocus()
		self.ui.markerFileField.setText(self.parent.markerFileName)
		self.ui.accountNameField.clearFocus()
		self.ui.accountNameField.setText(self.parent.accountName)
		self.ui.urlField.setFocus()
	
	def updateFeatureList(self,featureClass,filterFolderId):
		self.parent.updateFeatureList(featureClass,filterFolderId)
		
	def displayLocationCount(self):
		self.ui.locationCountLabel.setText(str(len(self.parent.addrTable))+" locations loaded")
		self.parent.ui.locationCountLabel.setText(str(len(self.parent.addrTable))+" locations loaded")

	def browseForMarkerFile(self):
		fileDialog=QFileDialog()
		fileDialog.setOption(QFileDialog.DontUseNativeDialog)
		fileDialog.setWindowFlags(Qt.WindowStaysOnTopHint)
#         fileDialog.setProxyModel(CSVFileSortFilterProxyModel(self))
		fileDialog.setNameFilter("CSV Marker Definition Files (*.csv)")
#         fileDialog.setDirectory(self.firstWorkingDir)
		if fileDialog.exec_():
			fileName=fileDialog.selectedFiles()[0]
			self.ui.markerFileField.setText(fileName)
			self.parent.markerFileName=fileName
		else: # user pressed cancel on the file browser dialog
			return

	def browseForLocationFile(self):
		fileDialog=QFileDialog()
		fileDialog.setOption(QFileDialog.DontUseNativeDialog)
		fileDialog.setWindowFlags(Qt.WindowStaysOnTopHint)
#         fileDialog.setProxyModel(CSVFileSortFilterProxyModel(self))
		fileDialog.setNameFilter("CSV Location Lookup Files (*.csv)")
#         fileDialog.setDirectory(self.firstWorkingDir)
		if fileDialog.exec_():
			fileName=fileDialog.selectedFiles()[0]
			self.ui.locationFileField.setText(fileName)
			self.parent.locationFileName=fileName
		else: # user pressed cancel on the file browser dialog
			return
		
	def reload(self):
#         self.parent.addrTable=[[]]
		self.parent.buildTableFromCsv(self.ui.locationFileField.text())
		self.displayLocationCount()
	
	def urlEditingFinished(self):
		url=self.ui.urlField.text()
		online="sartopo.com" in url.lower()
		self.ui.accountNameLabel.setEnabled(online)
		self.ui.accountNameField.setEnabled(online)
		if online: # in an online map, make sure account is specified, then try to create session
			if self.ui.accountNameField.text()!="":
				self.parent.createSTS()
			else:
				self.ui.accountNameField.setFocus()
		else: # if a local map, try to create the session immediately
			self.parent.createSTS()
	
	def folderComboBoxIndexChanged(self):
		self.parent.ui.existingMarkerComboBox.setCurrentIndex(0)

	# note: calling createSTS on editingFinished, which includes focusOut,
	#  causes failed link when tabbing out of the url field if the accountName
	#  field is next in tab sequence.  So, use textChanged instead.
	def accountNameTextChanged(self):
		an=self.ui.accountNameField.text()
		self.parent.accountName=an
		self.parent.createSTS()

	def markerFileEditingFinished(self):
		mf=self.ui.markerFileField.text()
		if not os.path.isfile(mf):
			warn=QMessageBox(QMessageBox.Warning,"Error","Specified marker definition file "+mf+" does not exist.",
					QMessageBox.Ok,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
			warn.show()
			warn.raise_()
			warn.exec_()
			return
		self.parent.markerFileName=mf

	def locationFileEditingFinished(self):
		lf=self.ui.locationFileField.text()
		if not os.path.isfile(lf):
			warn=QMessageBox(QMessageBox.Warning,"Error","Specified location file "+lf+" does not exist.",
					QMessageBox.Ok,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
			warn.show()
			warn.raise_()
			warn.exec_()
			return
		self.parent.locationFileName=lf
		
		
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