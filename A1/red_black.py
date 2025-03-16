# File:     red_black.py
# Author:   John Longley
# Date:     October 2022

# Template file for Inf2-IADS (2022-23) Coursework 1, Part B
# Implementation of dictionaries by red-black trees: space-saving version

# Provided code:

Red, Black = True, False


def colourStr(c):
    return 'R' if c == Red else 'B'


Left, Right = 0, 1


def opposite(branch):
    return 1 - branch


branchLabels = ['l', 'r']


class Node():

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.colour = Red
        self.left = None
        self.right = None

    def getChild(self, branch):
        if branch == Left:
            return self.left
        else:
            return self.right

    def setChild(self, branch, y):
        if branch == Left:
            self.left = y
        else:
            self.right = y

    def __repr__(self):
        return str(self.key) + ':' + str(self.value) + ':' + colourStr(self.colour)


# Use None for all trivial leaf nodes

def colourOf(x):
    if x is None:
        return Black
    else:
        return x.colour


class RedBlackTree():

    def __init__(self):
        self.root = None
        self.stack = []

    # TODO: Task 1.
    def lookup(self, key):
        # look up item from root
        curr = self.root
        return self.lookuphelper(curr, key)

    # use a helper function that can look up the given key from current Node to its leaves
    def lookuphelper(self, curr, key):
        # if the current node is none meaning that key is not in tree
        if curr is None:
            return None
        # if the current node's key is equal to key meaning that key has been found in tree
        if key == curr.key:
            return curr.value
        # search aimed key down one level
        if key < curr.key:
            return self.lookuphelper(curr.left, key)
        else:
            return self.lookuphelper(curr.right, key)

    # TODO: Task 2.
    def plainInsert(self, key, value):
        self.stack = []  # renew stack
        y = None  # use y to record the last compared node
        x = self.root  # use x to compare with given key
        # keep comparing until we find the node, or we reach the end of leaf
        while x is not None:
            y = x
            self.stack.append(x)
            # if given key is smaller than the key of node, then go left child and add branch into stack
            if key < x.key:
                x = x.left
                self.stack.append(0)
            # if given key is equal to the key of node, then we do not need to search down and replace y by new node
            elif key == x.key:
                y = Node(key, value)
                x = None
            # if given key is bigger than the key of node, then go right child and add branch into stack
            else:
                x = x.right
                self.stack.append(1)
        # y is none showing there is no node in tree
        if y is None:
            self.root = Node(key, value)
            self.stack.append(Node(key, value))
        # if new node is smaller, then put it at left of its parent y
        elif key < y.key:
            y.left = Node(key, value)
            self.stack.append(Node(key, value))
        # if new node is bigger, then put it at right of its parent y
        elif key > y.key:
            y.right = Node(key, value)
            self.stack.append(Node(key, value))

    # TODO: Task 3.
    def tryRedUncle(self):
        # if length of stack larger than five, then the node can have an uncle and a parent
        if len(self.stack) >= 5:
            # check whether the current node, its parent and its uncle are red
            if colourOf(self.stack[- 1]) == Red and \
                    colourOf(self.stack[- 5].right) == Red and \
                    colourOf(self.stack[- 5].left) == Red:
                # set the colour of current node's uncle to black
                self.stack[- 3].colour = Black
                # find whether current node's uncle's branch and set the colour of its uncle to black
                if self.stack[- 4] == 0:
                    self.stack[- 5].right.colour = Black
                if self.stack[- 4] == 1:
                    self.stack[- 5].left.colour = Black
                # set current node's grandparent to red
                self.stack[- 5].colour = Red
                # remove these three changed node and their branch from stack
                for i in range(4):
                    self.stack.pop()
                # if the node satisfy red-uncle rule, then return true
                return True
        # if the node does not satisfy red-uncle rule, then return false
        return False

    def repeatRedUncle(self):
        is_red_uncle = self.tryRedUncle()
        # apply the red-uncle rule till the node that does not satisfy red-uncle rule
        while is_red_uncle:
            is_red_uncle = self.tryRedUncle()

    # Provided code to support Task 4:

    def toNextBlackLevel(self, node):
        # inspect subtree down to the next level of blacks
        # and return list of components (subtrees or nodes) in L-to-R order
        # (in cases of interest there will be 7 components A,a,B,b,C,c,D).
        if colourOf(node.left) == Black:  # node.left may be None
            leftHalf = [node.left]
        else:
            leftHalf = self.toNextBlackLevel(node.left)
        if colourOf(node.right) == Black:
            rightHalf = [node.right]
        else:
            rightHalf = self.toNextBlackLevel(node.right)
        return leftHalf + [node] + rightHalf

    def balancedTree(self, comps):
        # build a new (balanced) subtree from list of 7 components
        [A, a, B, b, C, c, D] = comps
        a.colour = Red
        a.left = A
        a.right = B
        c.colour = Red
        c.left = C
        c.right = D
        b.colour = Black
        b.left = a
        b.right = c
        return b

    # TODO: Task 4.
    def endgame(self):
        # if the root is red, then turn it black
        if colourOf(self.root) == Red:
            self.root.colour = Black
        # if current node has grandparent, then we can check some
        # configuration involving a black with 4 'nearset black descendants'.
        if len(self.stack) > 4:
            # only the current node and its parent are red and its uncle is black will meet this situation
            # since we applied the red-uncle rule as much as possible, we do not need to check its uncle
            if colourOf(self.stack[- 1]) == Red and colourOf(self.stack[- 3]) == Red:
                # if the current node has grandpa Tai, then the new top need to connect to grandpa Tai.
                if len(self.stack) > 6:
                    connect = self.stack[- 7]  # the grandpa Tai is the connection to new top
                    currtop = self.balancedTree(self.toNextBlackLevel(self.stack[- 5]))  # new top of 7 nodes
                    connect.setChild(self.stack[- 6], currtop)
                # if the current 7 node contains the root of the tree, then just change the root of the tree.
                else:
                    self.root = self.balancedTree(self.toNextBlackLevel(self.stack[- 5]))

    # handle all situation after many times of red-uncle rule
    def insert(self, key, value):
        # insert the red node
        self.plainInsert(key, value)
        # fix the problem of red-uncle rule
        self.repeatRedUncle()
        # fix problem after red-uncle rule
        self.endgame()

    # Provided code:

    # Printing tree contents

    def __str__(self, x):
        if x == None:
            return 'None:B'
        else:
            leftStr = '[ ' + self.__str__(x.left) + ' ] '
            rightStr = ' [ ' + self.__str__(x.right) + ' ]'
            return leftStr + x.__str__() + rightStr

    def __repr__(self):
        return self.__str__(self.root)

    def showStack(self):
        return [x.__str__() if isinstance(x, Node) else branchLabels[x]
                for x in self.stack]

    # All keys by left-to-right traversal

    def keysLtoR_(self, x):
        if x == None:
            return []
        else:
            return self.keysLtoR_(x.left) + [x.key] + self.keysLtoR_(x.right)

    def keysLtoR(self):
        return self.keysLtoR_(self.root)


# End of class RedBlackTree


# Creating a tree by hand:

sampleTree = RedBlackTree()
sampleTree.root = Node(2,'two')
sampleTree.root.colour = Black
sampleTree.root.left = Node(1,'one')
sampleTree.root.left.colour = Black
sampleTree.root.right = Node(4,'four')
sampleTree.root.right.colour = Red
sampleTree.root.right.left = Node(3,'three')
sampleTree.root.right.left.colour = Black
sampleTree.root.right.right = Node(6,'six')
sampleTree.root.right.right.colour = Black


# For fun: sorting algorithm using trees
# Will remove duplicates

def TreeSort(L):
    T = RedBlackTree()
    for x in L:
        T.insert(x, None)
    return T.keysLtoR()

# End of file
