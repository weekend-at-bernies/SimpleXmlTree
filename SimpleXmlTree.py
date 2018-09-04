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
            # Throws xml.etree.ElementTree.ParseError if input xml is malformed (XML syntax error) or is empty file:
            self.et = xml.etree.ElementTree.parse(self.xmlfile) 
                 
        elif (create and len(root_tag) > 0):
            f = open(self.xmlfile, 'a+')
            root =  xml.etree.ElementTree.Element(root_tag)
            self.et = xml.etree.ElementTree.ElementTree(root)  
        else:
            # FIXME:
            raise IOError("Error: invalid arguments provided")     
        self.root = XmlNode(self.et.getroot())         
        f.close()
        

    def getRoot(self):
        return self.root


    # FIXME : WHAT IS THIS FUNCTION FOR PLEASE????
    # FIXME : change to write or append file?
    def update(self, indentwidth=2):
        f = open(self.xmlfile, 'w+') 
        f.write(self.root.dump(indentwidth))
        f.close()

    def __str__(self):
        return self.root.dump()
        

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

# A debugging class that is used by XmlNode.getLineage():
#
class RootTracer(XmlTreeVisitor):

    def __init__(self, tag=None):
        # Invoke the super (XmlTreeVisitor) class constructor:
        super(RootTracer, self).__init__(XmlTreeVisitorType.parentvisitor)
        self.map = []
        self.tag = tag

    def previsit_parentvisitor(self, node): 
        self.map.insert(0, node)
        if self.tag is not None:
            if self.tag == node.getTag():
                return self.map
           
    def postvisit_parentvisitor(self, node):  
        return self.map

##########################################################################################################################

# XML node 101:
#
# <MyTag attrib1='int' attrib2='50'>144</MyTag>
#
# MyTag : this is node tag (mandatory)
# 144 : this is node val (optional: when no val exists, the node is called an "empty tag")
# 'int, '50', ... : these are node attrib (optional)
#
class XmlNode(object):

    # 'tva' : tag, val, attrib 
    def __init__(self, node, tva=None): # tag=None, val=None):
        self.parent = None
        self.children = []

        # Create XmlNode from existing xml.etree.ElementTree.Element:
        if node is not None:
            self.node = node
            for c in self.node:
                n = XmlNode(c)
                n.parent = self
                self.children.append(n)

        # Else create a brand new XmlNode:
        elif tva is not None:

            # Will raise TypeError if this does not evaluate true: > type(tva) == list
            if len(tva) != 3:
                raise ValueError("Error: error message here")

            tag = tva[0] # Mandatory
            val = tva[1] # Optional (but must be string)
            attrib = tva[2] # Optional 

            self.node = xml.etree.ElementTree.Element(tag)
            if val is not None:
                self.node.text = val
                #if len(str(val).strip()) > 0:
                #    self.node.text = str(val).strip()

            # FIXME : process attribs
            if attrib is not None:
                pass
        else:
            # FIXME:
            raise ValueError("Error: error message here")

        

    #########################################################################################################
    # CORE NODE FUNCTIONALITY (tag, val, attrib)

    # Return the "MyTag" part of: <MyTag>val</MyTag>
    def getTag(self):
        return self.node.tag

    # Return the "val" part of: <MyTag>val</MyTag>
    # If empty tag (ie. val DNE), then return empty string.
    # FIXME: WHY IS STRIP() important?
    def getVal(self):
        if self.node.text is None:
            return ""
        else:
            return self.node.text.strip()

    # Suppose your node is like this: <country name="Australia" capital="Canberra> </country>
    # Then self.node.attrib is this dictionary: { ('name' : 'Australia') , ('capital' : 'Canberra') }
    # And this function will return a list of keys: [ 'name', 'capital' ]
    # Now use getAttribVal(attrib) to get the key-value.
    def getAttrib(self):
        return self.node.attrib.keys()

    def getAttribVal(self, attrib):
        return self.node.attrib.get(attrib, None)


    # Sets val of this node
    # FIXME: WHY IS STRIP() important?
    def setVal(self, val):
        if (len(str(val).strip()) > 0):
            self.node.text = str(val).strip()

    # FIXME: require functions: setTag() and setAttrib() ???

    #########################################################################################################
    # CORE NODE FUNCTIONALITY 

    # Make this class iterable, ie.
    # for node in self:
    #     ...
    # In this case return an iterator over the child nodes.
    def __iter__(self):
        return iter(self.children)

    # Returns the number of child nodes:
    def __len__(self):
        return len(self.children)

    #########################################################################################################
    # CORE DEBUG FUNCTIONALITY (pretty print functions)

    # Returns a string like this: <MyTag attrib1='int' attrib2='50'>144</MyTag>
    def __str__(self):
        s = ""
        s += "<%s"%(self.getTag())
        for attrib in self.getAttrib():
            s += " %s='%s'"%(attrib, self.getAttribVal(attrib))
        s += ">%s</%s>"%(self.getVal(), self.getTag())
        return s

    # Dumps valid XML rooted at this node
    def dump(self, indentwidth=2):
        return self.strformat1(indentwidth)

    # Dumps tag lineage back/from a specified node, or assumes root.
    # Example output:
    # [ <root> ] --> [ <tag1> ] --> [ <tag2> ] --> ... --> [ <this_node> ]
    def getLineage(self, rootTag=None, fromRoot=True):
        l = (RootTracer(rootTag)).visit(self)
        if not fromRoot:
            l.reverse()
        s = ""
        for n in l:
            if len(s) > 0:
                s += " --> " 
            s += "[ <%s> ]"%(n.getTag())
        return s

    def strformat1(self, indentwidth=2, indentcount=0):
        s = ""
        s += self.getIndentStr(indentwidth, indentcount) + "<%s"%(self.getTag())
        for attrib in self.getAttrib():
            s += " %s='%s'"%(attrib, self.getAttribVal(attrib))
        s += ">%s\n"%(self.getVal())
        for c in self:
            s += c.strformat1(indentwidth, (indentcount + 1))
        s += self.getIndentStr(indentwidth, indentcount) + "</%s>\n"%(self.getTag())
        return s
       
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
    # PUBLIC FUNCTIONALITY

    # Am I a root node (ie. I have no parent)?
    def isRoot(self):
        if self.parent is None:
            return True
        return False

    # Am I a parent node (ie. I have children)?
    def isParent(self):
        return len(self) > 0

    # Am I a childless node (ie. I have no children)?
    def isChildless(self):
        return not self.isParent()














    #########################################################################################################
    # PRIVATE TREE FUNCTIONALITY

    # FIXME: need a remove() (opposite to append), and dump()

    

    # Add children to this node.
    def add(self, children):
        for c in children:
            c.parent = self
            self.node.append(c.node)

    

    #########################################################################################################
    # PUBLIC TREE FUNCTIONALITY

    














    

    

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


    


    #def __eq__(self, obj):
    #    return isinstance(obj, XmlNode) and obj.node is self.node 

    




