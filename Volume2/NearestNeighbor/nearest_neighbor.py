# nearest_neighbor.py
import numpy as np
import sys
sys.path.insert(1,"./Trees")
from trees import BST
from trees import BSTNode
from scipy.spatial import KDTree
from sklearn import neighbors

def metric(x, y):
    """Return the Euclidean distance between the 1-D arrays 'x' and 'y'.

    Raises:
        ValueError: if 'x' and 'y' have different lengths.

    Example:
        >>> metric([1,2],[2,2])
        1.0
        >>> metric([1,2,1],[2,2])
        ValueError: Incompatible dimensions.
    """
    if len(x) != len(y):
        raise ValueError("Incompatible dimensions")
    return np.sqrt(sum((x-y)**2))


def exhaustive_search(data_set, target):
    """Solve the nearest neighbor search problem exhaustively. Check the distances between 'target' and each point in 'data_set'. Use the Euclidean metric to calculate distances.

    Parameters:
        data_set ((m,k) ndarray): An array of m k-dimensional points.
        target ((k,) ndarray): A k-dimensional point to compare to 'dataset'.

    Returns:
        ((k,) ndarray) the member of 'data_set' that is nearest to 'target'.
        (float) The distance from the nearest neighbor to 'target'.
    """
    first = True
    for k in data_set:
        if first:
            first = False
            shortestd = metric(k,target)
            breve = k
        else:
            d = metric(k,target)
            if d < shortestd:
                shortestd = d
                breve = k
    return breve,shortestd


class KDTNode(BSTNode):
    """a k-dimensional Node object. Used as a helper class for KDT, inherits from BSTNode"""
    def __init__(self,data):
        """Initialize the KDT Node
        
        Parameter:
            data (1,ndarray): ndarray to hold all of the n-dimensional data"""
        if type(data) is not np.ndarray:
            raise TypeError("Inserted data is not of type np.ndarray")
        self.value = data
        self.axis = 0
        self.right = None
        self.left = None
        self.prev = None
        
      
         
class KDT(BST):
    """A k-dimensional binary search tree object. Used to solve the nearest neighbor problem efficiently.

    Attributes:
        root (KDTNode): The root node of the tree. Like all other nodes in the
            tree, the root houses data as a NumPy array.
        k (int): The dimension of the tree (the 'k' of the k-d tree).
    """
    def __init__(self):
        """Initialize the KDT Tree"""
        self.root = None

    def find(self, data):
        """Return the node containing 'data'. If there is no such node in the tree, or if the tree is empty, raise a ValueError.
        """

        # Define a recursive function to traverse the tree.
        def _step(current):
            """Recursively step through the tree until the node containing 'data' is found. If there is no such node, raise a Value Error.
            """
            if current is None:                     # Base case 1: dead end.
                raise ValueError(str(data) + " is not in the tree")
            elif np.allclose(data, current.value):
                return current                      # Base case 2: data found!
            elif data[current.axis] < current.value[current.axis]:
                return _step(current.left)          # Recursively search left.
            else:
                return _step(current.right)         # Recursively search right.

        # Start the recursion on the root of the tree.
        return _step(self.root)

    def insert(self, data):
        """Insert a new node containing 'data' at the appropriate location.
        Return the new node. This method should be similar to BST.insert().
        """
        newNode = KDTNode(data)
        if self.root is None:
            self.root = newNode
        else:
            cNode = self.rInsert(self.root,newNode)
            newNode.axis = (cNode.axis +1)%len(newNode.value)
        return newNode
        
    def rInsert(self,cNode,nNode):
        """Recursive part of the Insert function
        
        Parameters:
            nNode (KDTNode): Node containing the requisite data
            dimension (int): Keeps track of which dimension we should be looking at
        """
        #if the all values in the nodes are equal, raise an error. Otherwise, if the current value is <= new value go right 
        if (nNode.value == cNode.value).all():                #If the node already exists in our tree
            raise ValueError("Nodes must be unique!")
        if nNode.value[cNode.axis] >= cNode.value[cNode.axis]:#We move down the right subtree
            if cNode.right is None:
                cNode.right,nNode.prev = nNode,cNode
                return cNode
            return self.rInsert(cNode.right,nNode)
                                                              #Otherwise, we move down the left
        if cNode.left is None:
            cNode.left,nNode.prev = nNode,cNode
            return cNode
        return self.rInsert(cNode.left,nNode)
        
    def remove(*args,**kargs):
        """Disables remove() to keep the tree intact"""
        raise NotImplementedError("remove() has been disabled from this class")


def nearest_neighbor(data_set, target):
    """Use your KDT class to solve the nearest neighbor problem.

    Parameters:
        data_set ((m,k) ndarray): An array of m k-dimensional points.
        target ((k,) ndarray): A k-dimensional point to compare to 'dataset'.

    Returns:
        The point in the tree that is nearest to 'target' ((k,) ndarray).
        The distance from the nearest neighbor to 'target' (float).
    """

    def KDTsearch(current, neighbor, distance):
        """The actual nearest neighbor search algorithm.

        Parameters:
            current (KDTNode): the node to examine.
            neighbor (KDTNode): the current nearest neighbor.
            distance (float): the current minimum distance.

        Returns:
            (ndarray): The new nearest neighbor in the tree.
            (float): The new minimum distance.
        """
        if current is None:                                     #Base case
            return neighbor,distance
        index = current.axis
        if metric(current.value,target)<distance:
            neighbor,distance = current,metric(current.value,target)  #Update the best estimate
        if target[index] < current.value[index]:                #Recurse left
            neighbor,distance = KDTsearch(current.left,neighbor,distance)
            if target[index]+distance >= current.value[index]:
                neighbor,distance = KDTsearch(current.right,neighbor,distance)
        else:                                                   #Recurse right
            neighbor,distance = KDTsearch(current.right,neighbor,distance)
            if target[index] - distance <= current.value[index]:
                neighbor,distance = KDTsearch(current.left,neighbor,distance)
        return neighbor, distance
        
    myKDT = KDT()
    for k in data_set:                                          #Add all of the data into the KDT
        myKDT.insert(k)
    c = myKDT.root
    a,b= KDTsearch(c,c,metric(c.value,target))
    return a.value,b



class KNeighborsClassifier(object):
    """A k-nearest neighbors classifier object. Uses SciPy's KDTree to solve
    the nearest neighbor problem efficiently.
    """

    def __init__(self, data, labels):
        """Initialize the training set and labels. Construct the KDTree from
        the training data.

        Parameters:
            data (ndarray): Training data.
            labels (ndarray): Corresponding labels for the training data.
        """
        self.data = data
        self.labels = labels

    def predict(self, testpoints, k):
        """Predict the label of a new data point by finding the k-nearest
        neighbors.

        Parameters:
            testpoints (ndarray): New data point(s) to label.
            k (int): Number of neighbors to find.
        """
        nbrs = neighbors.KNeighborsClassifier(n_neighbors=k,weights='distance',p=2)
        nbrs.fit(self.data,self.labels)
        return nbrs.predict(testpoints)
        
