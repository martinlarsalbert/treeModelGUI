
from PyQt4 import QtCore, QtGui


class TreeItem(object):
    
    def __init__(self,displayData,parent=None):
        self.parentItem = parent
        self.displayData = displayData
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.displayData)

    def displayData(self, column):
        """This function returns the data that should be displayed in the columns"""
        try:
            return self.displayData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0
        

class TreeModel(QtCore.QAbstractItemModel):
    
    def __init__(self,parent=None):
        
        super(TreeModel, self).__init__(parent)
        
        self.rootItem = TreeItem(("Title",))
        self.setupModelData(self.rootItem)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole:
            item = index.internalPointer()
            return item.displayData[index.column()]
        else:
            return None
        

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.displayData[section]

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
            
        
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()


    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

        
    def setupModelData(self,parent):
        
        self.buildTree(parent=parent, level=0, maxLevel=5, maxSiblings=5)
        
    def buildTree(self,parent,level=0,maxLevel=5,maxSiblings=5,nameString=""):
        
        
        if level < (maxLevel-1):
            for siblingCounter in range(maxSiblings):
                
                newNameString = nameString + str(siblingCounter)

                newDisplayData = (newNameString,)    
                
                newItem = TreeItem(displayData=newDisplayData,parent=parent)        
                parent.appendChild(newItem)
                
                #Add some children, grand children etc to the newItem:
                self.buildTree(parent=newItem, level = level + 1, maxLevel=maxLevel, maxSiblings=maxSiblings,nameString=newNameString)

        else:
            #Leaf level reached:
            newNameString = nameString + 'Leaf'
            newDisplayData = (newNameString,)    
            
            newItem = TreeItem(displayData=newDisplayData,parent=parent)        
            parent.appendChild(newItem)
                   

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    f = QtCore.QFile('default.txt')
    f.open(QtCore.QIODevice.ReadOnly)
    model = TreeModel()
    f.close()

    view = QtGui.QTreeView()
    view.setModel(model)
    view.setWindowTitle("Simple Tree Model")
    view.show()
    sys.exit(app.exec_())
    