# trees.py
from matplotlib import pyplot as plt
import numpy as np
import time

class SinglyLinkedListNode:
    """Simple singly linked list node."""
    def __init__(self, data):
        self.value, self.next = data, None

class SinglyLinkedList:
    """A very simple singly linked list with a head and a tail."""
    def __init__(self):
        self.head, self.tail = None, None

    def append(self, data):
        """Add a Node containing 'data' to the end of the list."""
        n = SinglyLinkedListNode(data)
        if self.head is None:
            self.head, self.tail = n, n
        else:
            self.tail.next = n
            self.tail = n

def iterative_search(linkedlist, data):
    """Search 'linkedlist' iteratively for a node containing 'data'.
    If there is no such node in the list, or if the list is empty,
    raise a ValueError.

    Inputs:
        linkedlist (SinglyLinkedList): a linked list.
        data: the data to search for in the list.

    Returns:
        The node in 'linkedlist' containing 'data'.
    """
    current = linkedlist.head
    while current is not None:
        if current.value == data:
            return current
        current = current.next
        
    raise ValueError(str(data) + " is not in the list.")

def recursive_search(linkedlist, data):
    """Search 'linkedlist' recursively for a node containing 'data'.
    If there is no such node in the list, or if the list is empty,
    raise a ValueError.

    Inputs:
        linkedlist (SinglyLinkedList): a linked list object.
        data: the data to search for in the list.

    Returns:
        The node in 'linkedlist' containing 'data'.
    """
    return rSearchHelp(linkedlist.head,data)

def rSearchHelp(cNode,data):
    if cNode == None:
        raise ValueError(str(data) + " is not in the list.")
    if cNode.value == data:
        return cNode
    
    return rSearchHelp(cNode.next,data)

class BSTNode:
    """A Node class for Binary Search Trees. Contains some data, a
    reference to the parent node, and references to two child nodes.
    """
    def __init__(self, data):
        """Construct a new node and set the data attribute. The other
        attributes will be set when the node is added to a tree.
        """
        self.value = data
        self.prev = None        # A reference to this node's parent node.
        self.left = None        # self.left.value < self.value
        self.right = None       # self.value < self.right.value


class BST:
    """Binary Search Tree data structure class.
    The 'root' attribute references the first node in the tree.
    """
    def __init__(self):
        """Initialize the root attribute."""
        self.root = None

    def find(self, data):
        """Return the node containing 'data'. If there is no such node
        in the tree, or if the tree is empty, raise a ValueError.
        """

        # Define a recursive function to traverse the tree.
        def _step(current):
            """Recursively step through the tree until the node containing
            'data' is found. If there is no such node, raise a Value Error.
            """
            if current is None:                     # Base case 1: dead end.
                raise ValueError(str(data) + " is not in the tree.")
            if data == current.value:               # Base case 2: data found!
                return current
            if data < current.value:                # Step to the left.
                return _step(current.left)
            else:                                   # Step to the right.
                return _step(current.right)

        # Start the recursion on the root of the tree.
        return _step(self.root)

    def insert(self, data):
        """Insert a new node containing 'data' at the appropriate location.
        Do not allow for duplicates in the tree: if there is already a node
        containing 'data' in the tree, raise a ValueError.

        Example:
            >>> b = BST()       |   >>> b.insert(1)     |       (4)
            >>> b.insert(4)     |   >>> print(b)        |       / \
            >>> b.insert(3)     |   [4]                 |     (3) (6)
            >>> b.insert(6)     |   [3, 6]              |     /   / \
            >>> b.insert(5)     |   [1, 5, 7]           |   (1) (5) (7)
            >>> b.insert(7)     |   [8]                 |             \
            >>> b.insert(8)     |                       |             (8)
        """
        if self.root is None:
            self.root = BSTNode(data)
            return
        def rInsert(cNode,data):
            if cNode.value == data:                           #if there's a node with this exact data...
                raise ValueError("Node containing data already exists!")
            if data > cNode.value:                            #If it's larger go right
                if cNode.right is None:
                    rNode = BSTNode(data)
                    cNode.right,rNode.prev = rNode,cNode
                    return
                return rInsert(cNode.right,data)
            #Otherwise, it's smaller, go left
            if cNode.left is None:
                lNode = BSTNode(data)
                cNode.left,lNode.prev = lNode,cNode
                return
            return rInsert(cNode.left,data)
        return rInsert(self.root,data)
        
    def remove(self, data):
        """Remove the node containing 'data'. Consider several cases:
            1. The tree is empty
            2. The target is the root:
                a. The root is a leaf node, hence the only node in the tree
                b. The root has one child
                c. The root has two children
            3. The target is not the root:
                a. The target is a leaf node
                b. The target has one child
                c. The target has two children
            If the tree is empty, or if there is no node containing 'data',
            raise a ValueError.

        Examples:
            >>> print(b)        |   >>> b.remove(1)     |   [5]
            [4]                 |   >>> b.remove(7)     |   [3, 8]
            [3, 6]              |   >>> b.remove(6)     |
            [1, 5, 7]           |   >>> b.remove(4)     |
            [8]                 |   >>> print(b)        |
        """
        def leftmost(node):
            """Returns the leftmost right node"""
            if node.left == None:
                return node
            return leftmost(node.left)
            
        if self.root is None:                           #If the tree is empty we can't do anything
            raise ValueError("Empty Tree")
        lNone,rNone = False,False
        theNode = self.find(data)
        if theNode.right is None:
            rNone = True
        if theNode.left is None:
            lNone = True
        
        if lNone and rNone:                             #if it's a leaf
            if self.root == theNode:                    #If this is the root
                self.root = None
            else:                                       #It's not the root
                if theNode.value > (theNode.prev).value:#It's on the right
                    (theNode.prev).right = None
                else:                                   #It's on the left
                    (theNode.prev).left = None
                theNode.prev = None
                
        elif lNone and not rNone:
            nNode = theNode.right
            rNode,lNode,pNode = nNode.right,nNode.left,theNode.prev       #grab the leftmost right child
            if self.root == theNode:
                self.root = nNode
            else:
                if theNode.value > pNode.value:#It's on the right
                    pNode.right = nNode                   
                else:                                   #It's on the left
                    pNode.left = nNode
            nNode.prev = pNode
            
        elif not rNone:                                #if it has a right child
            nNode,rNode,lNode,pNode = leftmost(theNode.right),theNode.right,theNode.left,theNode.prev   #grab the leftmost right child
            if nNode.value != rNode.value:             #In case this node is the subtree root's next in line
                nNode.prev.left = nNode.right
                if nNode.right is not None:
                    nNode.right.prev = nNode.prev
                nNode.right = rNode
                rNode.prev = nNode
            if self.root == theNode:                   #if it's the root
                self.root = nNode
            else:
                if theNode.value > pNode.value:        #It's on the right
                    pNode.right = nNode
                else:                                  #It's on the left
                    pNode.left = nNode
            nNode.left,nNode.prev = lNode,pNode        #Reatatching node pointers'
            if not lNone:                              #if the removed node has a left child
                lNode.prev = nNode
            theNode.prev,theNode.right,theNode.left= None,None,None           #Remove the node
        else:                                          #If it only has a left child
            pNode,lNode = theNode.prev,theNode.left
            if self.root == theNode:                   #if we're removing the root
                self.root = theNode.left
                theNode.left = None
            else:
                if theNode.value > pNode.value:        #It's on the right
                    pNode.right = lNode
                else:                                  #It's on the left
                    pNode.left = lNode
            lNode.prev = pNode
                
        return

    def __str__(self):
        """String representation: a hierarchical view of the BST.
        Do not modify this method, but use it often to test this class.
        (this method uses a depth-first search; can you explain how?)

        Example:  (3)
                  / \     '[3]          The nodes of the BST are printed out
                (2) (5)    [2, 5]       by depth levels. The edges and empty
                /   / \    [1, 4, 6]'   nodes are not printed.
              (1) (4) (6)
        """

        if self.root is None:
            return "[]"
        str_tree = [list() for i in range(_height(self.root) + 1)]
        visited = set()

        def _visit(current, depth):
            """Add the data contained in 'current' to its proper depth level
            list and mark as visited. Continue recusively until all nodes have
            been visited.
            """
            str_tree[depth].append(current.value)
            visited.add(current)
            if current.left and current.left not in visited:
                _visit(current.left, depth+1)
            if current.right and current.right not in visited:
                _visit(current.right, depth+1)

        _visit(self.root, 0)
        out = ""
        for level in str_tree:
            if level != list():
                out += str(level) + "\n"
            else:
                break
        return out


class AVL(BST):
    """AVL Binary Search Tree data structure class. Inherits from the BST
    class. Includes methods for rebalancing upon insertion. If your
    BST.insert() method works correctly, this class will work correctly.
    Do not modify.
    """
    def _checkBalance(self, n):
        return abs(_height(n.left) - _height(n.right)) >= 2

    def _rotateLeftLeft(self, n):
        temp = n.left
        n.left = temp.right
        if temp.right:
            temp.right.prev = n
        temp.right = n
        temp.prev = n.prev
        n.prev = temp
        if temp.prev:
            if temp.prev.value > temp.value:
                temp.prev.left = temp
            else:
                temp.prev.right = temp
        if n == self.root:
            self.root = temp
        return temp

    def _rotateRightRight(self, n):
        temp = n.right
        n.right = temp.left
        if temp.left:
            temp.left.prev = n
        temp.left = n
        temp.prev = n.prev
        n.prev = temp
        if temp.prev:
            if temp.prev.value > temp.value:
                temp.prev.left = temp
            else:
                temp.prev.right = temp
        if n == self.root:
            self.root = temp
        return temp

    def _rotateLeftRight(self, n):
        temp1 = n.left
        temp2 = temp1.right
        temp1.right = temp2.left
        if temp2.left:
            temp2.left.prev = temp1
        temp2.prev = n
        temp2.left = temp1
        temp1.prev = temp2
        n.left = temp2
        return self._rotateLeftLeft(n)

    def _rotateRightLeft(self, n):
        temp1 = n.right
        temp2 = temp1.left
        temp1.left = temp2.right
        if temp2.right:
            temp2.right.prev = temp1
        temp2.prev = n
        temp2.right = temp1
        temp1.prev = temp2
        n.right = temp2
        return self._rotateRightRight(n)

    def _rebalance(self,n):
        """Rebalance the subtree starting at the node 'n'."""
        if self._checkBalance(n):
            if _height(n.left) > _height(n.right):
                if _height(n.left.left) > _height(n.left.right):
                    n = self._rotateLeftLeft(n)
                else:
                    n = self._rotateLeftRight(n)
            else:
                if _height(n.right.right) > _height(n.right.left):
                    n = self._rotateRightRight(n)
                else:
                    n = self._rotateRightLeft(n)
        return n

    def insert(self, data):
        """Insert a node containing 'data' into the tree, then rebalance."""
        BST.insert(self, data)
        n = self.find(data)
        while n:
            n = self._rebalance(n)
            n = n.prev

    def remove(*args, **kwargs):
        """Disable remove() to keep the tree in balance."""
        raise NotImplementedError("remove() has been disabled for this class.")

def _height(current):
    """Calculate the height of a given node by descending recursively until
    there are no further child nodes. Return the number of children in the
    longest chain down.

    This is a helper function for the AVL class and BST.__str__().
    Abandon hope all ye who modify this function.

                                node | height
    Example:  (c)                  a | 0
              / \                  b | 1
            (b) (f)                c | 3
            /   / \                d | 1
          (a) (d) (g)              e | 0
                \                  f | 2
                (e)                g | 0
    """
    if current is None:
        return -1
    return 1 + max(_height(current.right), _height(current.left))


def CompareSpeeds():
    """Compare the build and search speeds of the SinglyLinkedList, BST, and
    AVL classes. For search times, use iterative_search(), BST.find(), and
    AVL.find() to search for 5 random elements in each structure. Plot the
    number of elements in the structure versus the build and search times.
    Use log scales if appropriate.
    """
    with open("english.txt",'r') as myFile:
        contents = list(set(myFile.read().split('\n')))
    cLen,slla,bsta,avla,sllf,bstf,avlf=len(contents),[],[],[],[],[],[]
    for i in range(50,2048,150):
        subList = [contents[x] for x in set(np.random.randint(0,cLen,i))]
        LL,B,A = SinglyLinkedList(),BST(),AVL()
        LLstart,BSTstart,AVLstart = [],[],[]
        for j in subList:
            start = time.time()
            LL.append(j)
            LLstart +=[time.time()-start]
            start = time.time()
            B.insert(j)
            BSTstart +=[time.time()-start]
            start = time.time()
            A.insert(j)
            AVLstart +=[time.time()-start]
            
        slla +=[sum(LLstart)]
        avla +=[sum(AVLstart)]
        bsta +=[sum(BSTstart)]
        FrandItems = [subList[y] for y in np.random.randint(0,len(subList),5)]
        LLstart,BSTstart,AVLstart = [],[],[]
        for j in FrandItems:
            start = time.time()
            iterative_search(LL,j)
            LLstart +=[time.time()-start]
            start = time.time()
            B.find(j)
            BSTstart +=[time.time()-start]
            start = time.time()
            A.find(j)
            AVLstart +=[time.time()-start]
            
        sllf +=[sum(LLstart)]
        avlf +=[sum(AVLstart)]
        bstf +=[sum(BSTstart)]
        
    plt.subplot(121)
    plt.plot(range(50,2048,150),slla, 'r-',label="SinglyLinkedList")
    plt.plot(range(50,2048,150),bsta, 'g-',label="BST")
    plt.plot(range(50,2048,150),avla, 'b-',label="AVL")    
    plt.title("Build")
    plt.ylabel("Seconds")
    plt.xlabel("Length of Trees")
    plt.legend(loc = "upper left")
    plt.subplot(122)
    plt.plot(range(50,2048,150),sllf, 'r-',label="SinglyLinkedList")
    plt.plot(range(50,2048,150),bstf, 'g-',label="BST")
    plt.plot(range(50,2048,150),avlf, 'b-',label="AVL")
    plt.title("Find")
    plt.legend(loc = "upper left")
    plt.ylabel("Seconds")
    plt.xlabel("Length of Trees")
    return plt.show()
        