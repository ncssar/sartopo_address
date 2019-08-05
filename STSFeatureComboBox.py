from PyQt5.QtWidgets import QComboBox

# since there is no onShowPopup or similar signal, the recommended
#  way to perform an action when the combobox is opened is to subclass
#  and overload showPopup:

class STSFeatureComboBox(QComboBox):
    def __init__(self,parent=None):
        self.parent=parent
        self.headerText="Select"
        self.featureClass=None
#         self.filterFolderId=None
        # self.filterFolderComboBox = ui combobox object
        #  that contains the id (in currentData) of the folder to filter with
        self.filterFolderComboBox=None
        super(STSFeatureComboBox,self).__init__(parent)
   
    def showPopup(self):
        ffid=None
        print("t1")
        if self.filterFolderComboBox:
            if self.filterFolderComboBox.currentText()!=self.filterFolderComboBox.headerText:
                ffid=self.filterFolderComboBox.currentData()
        print("Fitlering using folder id "+str(ffid))
        self.parent.updateFeatureList(self.featureClass,ffid)
        QComboBox.showPopup(self)
        # expand the drop-down list width to fit the longest choice
        #   from stackoverflow.com/questions/3151798
        self.view().setMinimumWidth(self.minimumSizeHint().width())
        
        
    # setItems: rebuild the list of selections; prepend with Edit and a separator;
    #  each item should be a sartopo feature name and its corresponding sartopo id
    def setItems(self,l):
        self.clear()
        self.addItem(self.headerText)
        self.insertSeparator(1)
        for i in l:
            self.addItem(i[0],i[1])
