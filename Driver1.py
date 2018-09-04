import os.path
import sys
import SimpleXmlTree
from SimpleXmlTree import XmlTreeVisitor
from SimpleXmlTree import XmlTreeVisitorType
import argparse



##########################################################################################################################

class Visitor1(XmlTreeVisitor):

    def __init__(self):
        # Invoke the super (XmlTreeVisitor) class constructor:
        super(Visitor1, self).__init__(XmlTreeVisitorType.depthfirst)

    def previsit_depthfirst(self, node): 
        print "PRE-VISIT DEPTH FIRST: %s"%(node)
           
    def postvisit_depthfirst(self, node):  
        print "POST-VISIT DEPTH FIRST: %s"%(node)

##########################################################################################################################

class Visitor2(XmlTreeVisitor):

    def __init__(self):
        # Invoke the super (XmlTreeVisitor) class constructor:
        super(Visitor2, self).__init__(XmlTreeVisitorType.breadthfirst)

    def previsit_breadthfirst(self, node): 
        print "PRE-VISIT BREADTH FIRST: %s"%(node)
           
    def postvisit_breadthfirst(self, node):  
        print "POST-VISIT BREADTH FIRST: %s"%(node)



parser = argparse.ArgumentParser(description='XML test 1')
parser.add_argument('-i','--input', help='Input file (xml file)', required=True, metavar='<input xml file>')
#parser.add_argument('-o','--output', help='Output file (randomized)', required=True, metavar='<output file>')
#parser.add_argument('-s','--seed', help='randomizer seed', required=False, metavar='<seed>')
#parser.add_argument('-n','--count', help='output file number of lines to generate', required=True, metavar='<count>')
args = vars(parser.parse_args())

#if args['seed'] is not None:
#    seed = int(args['seed'])
#else:
#    seed = None


# Will raise exception if XML syntax errors are found:
xml = SimpleXmlTree.SimpleXmlTree(args['input'])
print xml

visitor1 = Visitor1()
visitor1.visit(xml.getRoot())

print ""

visitor2 = Visitor2()
visitor2.visit(xml.getRoot())


        #tracer = MetaVarXMLSpecTracer()

        # Will raise exception if semantic errors found:
        #tracer.visit(xml.getRoot())

        #self.mv_bin = MetaVariableBin(tracer.l_mv)

        #print self
        #print self.getRandom()









