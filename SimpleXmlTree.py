import xml.etree.ElementTree
import os
import copy

# FIXME: re-work this/suggest a HOW TO based on SPECIFIC host system eg. Python 2.7.X on Ubuntu 18.04 LTS.
# DEPENDENCY for PYTHON 2.7.X users:
# $ (sudo) pip install enum34:
# WARNINGS: - do NOT install 'enum'       : FIXME: not sure what you are referring to here??? python-enum ???
#           - do not SELF-UPDATE pip (ie. pip --update)           : FIXME: why not? does it break everything you have installed previously?
from enum import Enum

##########################################################################################################################

# WISH LIST/FIX ME list:
# A XmlSemanticError class for raising semantic errors in XML (where syntax is fine)
#
# BIG PROBLEM: Need to address node equivalencies. Currently whenever you enumerate the children of a node, it will create
# a whole new set of objects for those children. This has implications for when you want to do stuff like: currentNode is targetNode

##########################################################################################################################

class SimpleXmlTree(object):

    # If you want to create a new .xml:
    # - set create to True
    # - define your root_tag (eg. <node> in above)
    def __init__(self, xmlfile, create=False, root_tag=""):
        self.xmlfile = xmlfile
   
        # Check that file exists:
        if os.path.exists(self.xmlfile):
            # Check we have R/W access:
            f = open(self.xmlfile, 'rw')  
            # Throws xml.etree.ElementTree.ParseError if input xml is malformed or empty file:
            self.et = xml.etree.ElementTree.parse(self.xmlfile) 
                 
        elif (create and len(root_tag) > 0):
            f = open(self.xmlfile, 'a+')
            root =  xml.etree.ElementTree.Element(root_tag)
            self.et = xml.etree.ElementTree.ElementTree(root)  
        else:
            # FIXME:
            raise IOError("Error: invalid arguments provided")     
          
        f.close()
        

    def getRoot(self):
        return XmlNode(self.et.getroot())


    # FIXME : change to write or append file?
    def update(self, indentwidth=2):
        f = open(self.xmlfile, 'w+') 
        f.write(self.getRoot().dump(indentwidth))
        f.close()

    def __str__(self):
        return self.getRoot().dump()
        

##########################################################################################################################

class XmlTreeVisitorType(Enum):
    singlevisitor = 0
    parentvisitor = 1
    depthfirst = 2
    breadthfirst = 3

    def __str__(self):
        if (self == XmlTreeVisitorType.singlevisitor):
            return "singlevisitor"
        elif (self == XmlTreeVisitorType.parentvisitor):
            return "parentvisitor"
        elif (self == XmlTreeVisitorType.depthfirst):
            return "depthfirst"
        elif (self == XmlTreeVisitorType.breadthfirst):
            return "breadthfirst"
        else:
            return None 


class XmlTreeVisitor(object):

    def __init__(self, visitortype):
        self.visitortype = visitortype
       # print("%s %s"%(type(self.visitortype), XmlTreeVisitorType.singlevisitor))
 

    #def __init__(self, visitortype, ignore_tags=None, inverse=False):
    #    self.visitortype = visitortype
    #    if ignore_tags is not None:
    #        self.ignore_tags = ignore_tags              # The tags of nodes to ignore
    #    else:
    #        self.ignore_tags = []
    #    self.inverse = inverse                          # Inverse ignore, ie. the ignore_tags becomes 'support_only' tags  
   
    def getPreVisitFuncStr(self):
        return "previsit_%s"%(str(self.visitortype))
       # return "previsit_%s"%(self.visitortype.toString())
       # return "previsit_%s"%(self.visitortype)

    def getPostVisitFuncStr(self):
        return "postvisit_%s"%(str(self.visitortype))

    def previsit(self, node):
        if hasattr(self, self.getPreVisitFuncStr()):             
            f = getattr(self, self.getPreVisitFuncStr())
            return f(node)

    def postvisit(self, node):
        if hasattr(self, self.getPostVisitFuncStr()):   
            f = getattr(self, self.getPostVisitFuncStr())
            return f(node)  

    #def isVisiting(self, node):
    #    b = False
    #    if node.getTag() not in self.ignore_tags:
    #        b = True
    #    if not self.inverse:
    #        return b
    #    return not b

    def visit(self, node):
        if self.visitortype == XmlTreeVisitorType.breadthfirst:
            self.doBreadthFirstVisit(node)
        elif ((self.visitortype == XmlTreeVisitorType.depthfirst) or
            (self.visitortype == XmlTreeVisitorType.parentvisitor) or
            (self.visitortype == XmlTreeVisitorType.singlevisitor)):
            return self.doRecursiveVisit(node)

   # def visit(self, node):
   #     if self.isVisiting(node):
   #         if self.visitortype == XmlTreeVisitorType.breadthfirst:
   #             self.doBreadthFirstVisit(node)
   #         elif ((self.visitortype == XmlTreeVisitorType.depthfirst) or
   #               (self.visitortype == XmlTreeVisitorType.parentvisitor) or
   #               (self.visitortype == XmlTreeVisitorType.singlevisitor)):
   #             return self.doRecursiveVisit(node)
            
       
    # FIX ME : not sure where postvisit() should go, or how this will fare
    # with ignore tags, also implement return value!
    def doBreadthFirstVisit(self, node):
        visited = []
        queue = []

        queue.append(node)
        visited.append(node.node)

        # Pre-visit this node
        self.previsit(node)

        while len(queue) > 0:
            n1 = queue[0]
            queue = queue[1:]

            adjacent = n1.getAdjacent()
            for n2 in adjacent:
                if n2.node not in visited:                            
                    visited.append(n2.node)
                    queue.append(n2)

                    # Pre-visit this node
                    self.previsit(n2)


    def doRecursiveVisit(self, node):
        # Pre-visit this node
        r = self.previsit(node)
        if r is not None:
            return r 

        if self.visitortype == XmlTreeVisitorType.parentvisitor:
            if node.parent is not None:
                r = self.doRecursiveVisit(node.parent)
                if r is not None:
                    return r

        elif self.visitortype == XmlTreeVisitorType.depthfirst:
            for c in node:
                r = self.doRecursiveVisit(c)
                if r is not None:
                    return r

        # Post-visit this node
        r = self.postvisit(node)
        if r is not None:
            return r  

##########################################################################################################################

# A sample tree visitor implementation for debugging purposes:

# FIXME: describe how to implement

class RootTracer(XmlTreeVisitor):

    def __init__(self, tag=None):
        # Invoke the super (XmlTreeVisitor) class constructor:
        super(RootTracer, self).__init__(XmlTreeVisitorType.parentvisitor)
        self.map = []
        self.tag = tag

    def previsit_parentvisitor(self, node): 
        self.map.insert(0, node)
        if (self.tag is not None) and (self.tag == node.getTag()):
            return self.map
           
    def postvisit_parentvisitor(self, node):  
        return self.map

##########################################################################################################################

class XmlNode(object):

    def __init__(self, node, tag=None, val=None):
        self.parent = None
        # Create XmlNode from existing xml.etree.ElementTree.Element:
        if node is not None:
            self.node = node
        # Else create a brand new XmlNode:
        elif tag is not None:
            self.node = xml.etree.ElementTree.Element(tag)
            if val is not None:
                if len(str(val).strip()) > 0:
                    self.node.text = str(val).strip()
        else:
            # FIXME:
            raise Exception

    #########################################################################################################
    # PRIVATE TREE FUNCTIONALITY

    # FIXME: need a remove() (opposite to append), and dump()

    # Make this class iterable, ie.
    # for node in self:
    #     ...
    def __iter__(self):
        # This is cool: return an iterator of XmlNode objects, each one instantiated from the iterable self.node!
        #return iter(map(XmlNode, self.node))
        children = []
        for n in self.node:
            node = XmlNode(n)
            node.parent = self
            children.append(node)
        return iter(children)

    def __len__(self):
        return len(self.node)

    def __str__(self):
        # FIXME: need to print any 'attrib' as well
       # return "<%s>%s</%s>"%(self.getTag(), self.getVal(), self.getTag())
        s = ""
        s += "<%s"%(self.getTag())
        for attrib in self.getAttrib():
            s += " %s='%s'"%(attrib, self.getAttribVal(attrib))
        s += ">"
        if self.hasVal():
            s += "%s"%(self.getVal()) 
        s += "</%s>"%(self.getTag())
        
        return s

    def strformat1(self, indentwidth=2, indentcount=0):
        s = ""
        s += self.getIndentStr(indentwidth, indentcount) + "<%s"%(self.getTag())
        for attrib in self.getAttrib():
            s += " %s='%s'"%(attrib, self.getAttribVal(attrib))
        s += ">"

        if self.hasVal():
            s += "%s"%(self.getVal()) 
        s += "\n"
        for c in self:
            s += c.strformat1(indentwidth, (indentcount + 1))
        s += self.getIndentStr(indentwidth, indentcount) + "</%s>\n"%(self.getTag())
        return s

    # Add children to this node.
    def add(self, children):
        for c in children:
            c.parent = self
            self.node.append(c.node)


    # Suppose your node is like this: <country name="Australia" capital="Canberra> </country>
    # Then self.node.attrib is this dictionary: { ('name' : 'Australia') , ('capital' : 'Canberra') }
    # And this function will return a list of keys: [ 'name', 'capital' ]
    # Now use getAttribVal(attrib) to get the key-value.
    def getAttrib(self):
        return self.node.attrib.keys()

    def getAttribVal(self, attrib):
        return self.node.attrib.get(attrib, None)

    def hasAttrib(self, attrib=None):
        if None is attrib:
            if len(self.node.attrib.keys()) > 0:
                return True
        elif self.getAttribVal(attrib) is not None:
            return True
        return False
            
        # FIX ME has attrib 

    def getIndentStr(self, indentwidth, indentcount):
        s1 = ""
        s2 = ""
        i = 0     
        while i < indentwidth:
            s1 += " "
            i += 1
        i = 0 
        while i < indentcount:
            s2 += s1
            i += 1
        return s2

    #########################################################################################################
    # PUBLIC TREE FUNCTIONALITY

    # Return the "node" part of: <node> val </node>
    def getTag(self):
        return self.node.tag

    # Return the "val" part of: <node> val </node>
    def getVal(self):
        return self.node.text.strip()

    # Sets val of this node
    def setVal(self, val):
        if (len(str(val).strip()) > 0):
            self.node.text = str(val).strip()

    # Is there a "val" part of:<node> val </node>
    # A whitespace val will return: False
    def hasVal(self):
        if self.node.text is None:
            return False
        elif len((self.node.text).strip()) == 0:
            return False
        return True

    # Dumps valid .xml
    def dump(self, indentwidth=2):
        return self.strformat1(indentwidth)

    # Am I a root node (ie. I have no parent)?
    def isRoot(self):
        if self.parent is None:
            return True
        return False

    # Am I a parent node (ie. I have children)?
    def isParent(self):
        if len(self) > 0:
            return True
        return False

    # Am I a child node (ie. I have no children)?
    def isChild(self):
        return not self.isParent()

    # Return my parent.
    def getParent(self):
        return self.parent

    # Return the first child node with a given tag, and (optionally) val.
    def getChild(self, tag, val=None):
        for c in self:
            if c.getTag() == tag:
                if val is None:
                    return c
                elif c.hasVal():
                    if str(val) == c.getVal():
                        return c
        return None

    # Do I have a child node of given tag, and (optionally) val?
    def hasChild(self, tag, val=None):
        c = self.getChild(tag, val)
        if c is None:
            return False
        return True
 
    # Return a list of all children nodes or ones with a given tag.
    def getChildren(self, tag=None):
        children = []
        for c in self:
            if (c.getTag() == tag) or (tag is None):
                children.append(c)
        return children

    # Return the count of all children nodes or ones with a given tag.
    def getChildCount(self, tag=None):
        return len(self.getChildren(tag))

    # Return the val of the first child node found with a given tag.
    def getChildVal(self, tag):
        c = self.getChild(tag)
        if c is not None:
            return c.getVal()        # FIXME : should be .strip() ??
        return None


    # Adds a single child node.
    def addChild(self, node, tag=None, val=None):
        if node is not None:
            self.add([node])
        elif tag is not None:
            self.add([XmlNode(None, tag, val)])

    


    #########################################################################################################
    # EXTENDED/ADVANCED TREE FUNCTIONS

    # Return a list of my siblings.
    def getSiblings(self):
        siblings = []
        if self.parent is None:
            for c in self.parent:
                if c is not self:
                    siblings.append(c)
        return siblings


    # Return a list of parent + children (ie. adjacent nodes)
    def getAdjacent(self):
        adjacent = self.getChildren()
        if self.parent is not None:
            adjacent.append(self.parent)
        return adjacent
        

    # Gets an existing child node or creates/adds/returns one.
    def getOrAddChild(self, tag, val=None):
        c = self.getChild(tag, val)
        if c is None:
            c = XmlNode(None, tag, val)
            self.add([c])
        return c

    # Gets a grandchild node of given tag (first one found) and optionally val.
    def getGrandChild(self, tag, val=None):
        grandChild = None
        for c in self:
            grandChild = c.getChild(tag, val)
            if grandChild is not None:
                break
        return grandChild

    # Has a grandchild node of given tag (first one found) and optionally val?
    def hasGrandChild(self, tag, val=None):
        grandChild = self.getGrandChild(tag, val)
        if grandChild is None:
            return False
        return True

    # Returns a copy of this node (and its subtree):
    def clone(self):
        return XmlNode(copy.deepcopy(self.node))


    # Example output (where <projects> is root):
    # [ <projects> ] --> [ <project='bopeep'> ] --> [ <decode> ] --> [ <session='0'> ] --> [ <set='4'> ] --> [ <matrix='1'> ] --> [ <row='0'> ] --> [ <QR='3'> ]
    def getLineage(self, rootTag=None, fromRoot=True):
        forebears = (RootTracer(rootTag)).visit(self)
        if not fromRoot:
            forebears.reverse()
        s = ""
        for n in forebears:
            if len(s) > 0:
                s += " --> " 
            s += "[ <%s"%(n.getTag())
            if n.hasVal():
                s += "='%s'"%(n.getVal())
            s += "> ]"
        return s


    def __eq__(self, obj):
        return isinstance(obj, XmlNode) and obj.node is self.node 

    




