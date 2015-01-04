
from PyQt4 import QtGui
from PyQt4 import QtCore

import treeModel
from copy import deepcopy

# ---------------------------------------------------------------------
class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)

        self.resize(600,400)
        self.setWindowTitle("Treeview Example")

        #self.treeview = QtGui.QTreeView(self)
        
        self.model = treeModel.TreeModel()
        
        self.treeview = MyTreeView(self,model=self.model)
            
        self.setCentralWidget(self.treeview)


class MyTreeView(QtGui.QTreeView): 

    def __init__(self, parent=None, model=None): 
        super(MyTreeView, self).__init__(parent) 

        self.setModel(model) 
        
        self.myModel = model
        
        self.dragEnabled() 
        self.acceptDrops() 
        self.showDropIndicator() 
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove) 

        self.connect(self.model(), QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.change) 
        #self.expandAll() 
        
        self.doubleClicked.connect(self.on_treeview_clicked)
        
        #Context menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        
        #Node that has been cut:
        self.cutIndex = None
        self.copyIndex = None
        
    def change(self, topLeftIndex, bottomRightIndex): 
        self.update(topLeftIndex)
        #self.expandAll() 
        self.expand(topLeftIndex)
        self.expanded() 

    def expanded(self): 
        for column in range(self.model().columnCount(QtCore.QModelIndex())): 
            self.resizeColumnToContents(column)
            
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_treeview_clicked(self, index):
        """This functions retrieves a treeItem that is double clicked
        The @QtCore.pyqtSlot decorator seems unecessary but is keeps anyway
        """
        
        treeItem = index.internalPointer()        
        displayData = treeItem.displayData
        
        print(displayData[0])
    
    
    def openMenu(self, position):
        
        self.popup_menu = QtGui.QMenu(parent=self)
        self.popup_menu.addAction("New", self.new)
        self.popup_menu.addAction("Rename", self.new)
        self.popup_menu.addSeparator()
        
        self.popup_menu.addAction("Copy", self.copy)
        self.popup_menu.addAction("Cut", self.cut)
        self.popup_menu.addAction("Paste", self.paste)
        self.popup_menu.addSeparator()
        
        self.popup_menu.addAction("Delete", self.deleteItem)
        
        self.popup_menu.exec_(self.viewport().mapToGlobal(position))
      
        
    def new(self):
        """Unfinnished"""
        currentIndex = self.currentIndex()
        currentItem = currentIndex.internalPointer()
        
        print currentItem.displayData[0]
    
    def cut(self):
        """Cut a node"""
        self.cutIndex = self.currentIndex()
        self.copyIndex = None
        
    def copy(self):
        """Copy a node"""
        self.cutIndex = None
        self.copyIndex = self.currentIndex()
        
    def paste(self):
        """Paste a node
        A node is pasted before the selected destination node
        """
        
        sourceIndex = None
        if self.cutIndex != None:
            sourceIndex = self.cutIndex
        elif self.copyIndex != None:
            sourceIndex = self.copyIndex
            
        if sourceIndex != None:
        
            destinationIndex = self.currentIndex()
            destinationItem = destinationIndex.internalPointer()
            destinationParent = destinationItem.parent
            destinationParentIndex = self.myModel.parent(index=destinationIndex)
            
            
            sourceItem = sourceIndex.internalPointer()
            sourceRow = sourceItem.row()
            
            sourceParentIndex = self.myModel.parent(index=sourceIndex)
            
            row = destinationItem.row()
            
            if self.cutIndex != None:              
                self.myModel.moveItem(sourceParentIndex=sourceParentIndex,
                                      sourceRow=sourceRow,
                                      destinationParentIndex=destinationParentIndex,
                                      destinationRow = row)
            else:
                self.myModel.copyItem(sourceParentIndex=sourceParentIndex,
                                      sourceRow=sourceRow,
                                      destinationParentIndex=destinationParentIndex,
                                      destinationRow = row)

    
    def deleteItem(self):
        """Deletes the current item (node)"""
        
        currentIndex = self.currentIndex()
        currentItem = currentIndex.internalPointer()
        
        quitMessage = "Are you sure that %s should be deleted?" % currentItem.displayData
        messageBox = QtGui.QMessageBox(parent=self)
        
        
        reply = messageBox.question(self, 'Message', 
                     quitMessage, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            #This item is this row at its parents child list:
            row = currentItem.row()
        
            parentIndex = self.myModel.parent(index = currentIndex)
        
            self.myModel.removeRow(row=row,parentIndex=parentIndex)
            

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
