
from PyQt4 import QtGui
from PyQt4 import QtCore

import treeModel

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

# ---------------------------------------------------------------------
    
    

# ---------------------------------------------------------------------

class MyTreeView(QtGui.QTreeView): 

    def __init__(self, parent=None, model=None): 
        super(MyTreeView, self).__init__(parent) 

        self.myModel = model 
        self.setModel(self.myModel) 

        self.dragEnabled() 
        self.acceptDrops() 
        self.showDropIndicator() 
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove) 

        self.connect(self.model(), QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.change) 
        #self.expandAll() 
        
        self.doubleClicked.connect(self.on_treeview_clicked)

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


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
