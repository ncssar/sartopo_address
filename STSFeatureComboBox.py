#  this class defines an live-update / auto-update combo box; whenever the combo
#   box is opened, it rebuilds and displays the list of all sartopo features
#   of the associated feature type in the map associated with the open sartopo session

#  to create a live-update combo box, follow these steps:
#   1. if using Qt Designer, create a combo box and promote it to STSFeatureComboBox
#   2. in code, define a function updateFeatureList to retrieve the list; it will be called
#       automatically when the combo box popup is shown, in this class's overridden showPopup

# TODO: right now, functions used to rebuild the combo box are split between
#  this class and the calling class.  See if that can be simplified, to bring all
#  functionality into this class.


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
        self.extraItems=[] # list of extra items to add even if they do not exist on the map
        super(STSFeatureComboBox,self).__init__(parent)
   
    def showPopup(self):
        ffid=None
#         print("t1")
        if self.filterFolderComboBox:
            if self.filterFolderComboBox.currentText()!=self.filterFolderComboBox.headerText:
                ffid=self.filterFolderComboBox.currentData()
        print("Filtering using folder id "+str(ffid))
        # also pass self as the widget to call setItems on
        # self.parent.updateFeatureList(self.featureClass,ffid,self)
        self.parent.updateFeatureList(self.featureClass,ffid)
        for i in self.extraItems:
            if i not in [self.itemText(i) for i in range(self.count())]:
                self.addItem(i)
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
