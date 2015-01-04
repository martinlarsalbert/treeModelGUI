
from PyQt4 import QtCore, QtGui
import cPickle
from copy import deepcopy

class TreeItem(object):
    
    def __init__(self,displayData,parent=None):
        self.parent = parent
        self.displayData = displayData
        self.children = []

    def appendChild(self, item):
        self.children.append(item)
        
    def insertChild(self,item,row):
        item.parent = self
        self.children.insert(row,item)
        
    def removeChild(self, row): 
        value = self.children[row] 
        self.children.remove(value)
        
    def removeChildAtRow( self, row ):
        '''Removes an item at the given index from the list of children.'''
        self.children.pop( row ) 

    def child(self, row):
        return self.children[row]

    def childCount(self):
        return len(self.children)

    def columnCount(self):
        return len(self.displayData)

    def displayData(self, column):
        """This function returns the data that should be displayed in the columns"""
        try:
            return self.displayData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parent

    def row( self ):
        '''Get this item's index in its parent item's child list.'''
        if self.parent:
            return self.parent.children.index( self )
        return 0
        

class TreeModel(QtCore.QAbstractItemModel):
    
    def __init__(self,parent=None):
        
        super(TreeModel, self).__init__(parent)
        
        self.root = TreeItem(("Title",))
        self.setupModelData(self.root)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole:
            item = index.internalPointer()
            return item.displayData[index.column()]
        else:
            return None
        

    def flags( self, index ):
        '''Valid items are selectable, editable, and drag and drop enabled. Invalid indices (open space in the view)
        are also drop enabled, so you can drop items onto the top level.
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled
         
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsDragEnabled |\
               QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.root.displayData[section]

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parent = self.root
        else:
            parent = parent.internalPointer()
            
        
        childItem = parent.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()
    
    def parent( self, index ):
        '''Returns a QMoelIndex for the parent of the item at the given index.'''
        item = self.itemFromIndex( index )
        parent = item.parent
        if parent == self.root:
            return QtCore.QModelIndex()
        return self.createIndex( parent.row(), 0, parent )

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent = self.root
        else:
            parent = parent.internalPointer()

        return parent.childCount()
    
    def supportedDropActions( self ):
        '''Items can be moved and copied (but we only provide an interface for moving items in this example.'''
        return QtCore.Qt.MoveAction | QtCore.Qt.CopyAction
   
    def flags( self, index ):
        '''Valid items are selectable, editable, and drag and drop enabled. Invalid indices (open space in the view)
        are also drop enabled, so you can drop items onto the top level.
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled
         
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsDragEnabled |\
               QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def mimeTypes( self ):
        '''The MimeType for the encoded data.'''
        types = QtCore.QStringList( 'application/x-pynode-item-instance' )
        return types
    
    def mimeData( self, indices ):
        '''Encode serialized data from the item at the given index into a QMimeData object.'''
        data = ''
        item = self.itemFromIndex( indices[0] )
        try:
            data += cPickle.dumps( item )
        except:
            pass
        mimedata = QtCore.QMimeData()
        mimedata.setData( 'application/x-pynode-item-instance', data )
        return mimedata

    def dropMimeData( self, mimedata, action, row, column, parentIndex ):
        '''Handles the dropping of an item onto the model.
         
        De-serializes the data into a TreeItem instance and inserts it into the model.
        '''
        if not mimedata.hasFormat( 'application/x-pynode-item-instance' ):
            return False
        item = cPickle.loads( str( mimedata.data( 'application/x-pynode-item-instance' ) ) )
    
        
        dropParent = self.itemFromIndex( parentIndex )
        
        #The parent has to be changed to dropParent:
        item.parent = dropParent
        
        dropParent.appendChild( item )
        
        self.insertRows( dropParent.childCount()-1, 1, parentIndex )
        self.dataChanged.emit( parentIndex, parentIndex )
        return True
    
    def moveItem(self,sourceParentIndex,sourceRow,destinationParentIndex,destinationRow):
        """Move an item from sourceParentIndex, sourceRow to 
        destinationParentIndex, destinationRow"""
        
        sourceItemIndex = self.index(row=sourceRow, column=0, parent=sourceParentIndex)
        sourceItem = deepcopy(self.itemFromIndex(index=sourceItemIndex))
                
        #Insert source in destination:
        destinationParent = self.itemFromIndex(destinationParentIndex)
        sourceItem.parent = destinationParent
        destinationParent.insertChild(item=sourceItem,row=destinationRow)
        
        #Remove source:
        sourceParent = self.itemFromIndex(sourceParentIndex)
        sourceParent.removeChildAtRow(row=sourceRow+1)
        
        self.beginMoveRows(sourceParentIndex, sourceRow, sourceRow, destinationParentIndex, destinationRow)
        self.endMoveRows()
        
        self.dataChanged.emit( destinationParentIndex, destinationParentIndex )
    
    def copyItem(self,sourceParentIndex,sourceRow,destinationParentIndex,destinationRow):
        """Copy an item from sourceParentIndex, sourceRow to 
        destinationParentIndex, destinationRow"""
        
        sourceItemIndex = self.index(row=sourceRow, column=0, parent=sourceParentIndex)
        sourceItem = deepcopy(self.itemFromIndex(index=sourceItemIndex))
                
        #Insert source in destination:
        destinationParent = self.itemFromIndex(destinationParentIndex)
        sourceItem.parent = destinationParent
        destinationParent.insertChild(item=sourceItem,row=destinationRow)
                
        self.beginMoveRows(sourceParentIndex, sourceRow, sourceRow, destinationParentIndex, destinationRow)
        self.endMoveRows()
        
        self.dataChanged.emit( destinationParentIndex, destinationParentIndex )
        
    def insertRow(self, row, parent): 
        return self.insertRows(row, 1, parent) 
    
    def insertRows( self, row, count, parentIndex):
        '''Add a number of rows to the model at the given row and parent.'''
        self.beginInsertRows( parentIndex, row, row+count-1 )
        self.endInsertRows()
        return True

    def removeRow(self, row, parentIndex): 
        return self.removeRows(row, 1, parentIndex) 
    
    def removeRows( self, row, count, parentIndex ):
        '''Remove a number of rows from the model at the given row and parent.'''
        self.beginRemoveRows( parentIndex, row, row+count-1 )
        parent = self.itemFromIndex( parentIndex )
        for x in range( count ):
            parent.removeChildAtRow( row )
        self.endRemoveRows()
        return True
 
    def itemFromIndex(self, index): 
        return index.internalPointer() if index.isValid() else self.root 

        
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

    