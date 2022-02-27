from Parsing.Tree.Tree import Tree
from Parsing.ParseTree.ParseNode import ParseNode

class ParseTree(Tree):
    def __init__(self) -> None:
        super().__init__()
        
        self.shouldMark = False
        self.currentMarkingPosition = 0
        self.markedNodeMap = {}
        self.grammarMap = {}
       
    def insertNode(self, node: ParseNode) -> None:
        
        super().insertNode(node)
        
        if self.shouldMark:
            self.markedNodeMap[self.currentMarkingPosition].append(node.id)
    
    def addReferenceToGrammarMap(self) -> None:
        self.grammarMap[self.currentNode.nodeName] = self.currentNode
        
    def resetGrammarMap(self) -> None:
        for nodeName in self.grammarMap.keys():
            self.grammarMap[nodeName] = None
         
    def goTo(self, nodeName) -> None:
        if (nodeName in self.grammarMap):
            self.currentNode = self.grammarMap[nodeName]
        else:
            raise Exception("This grammar node wasn't found")    
    
    def postOrderTraversal(self, func) -> None:
        self.rootNode.postOrderTraversal(func)      
    
    def startMarking(self, currentMarkingPosition) -> None:
        self.shouldMark = True
        self.currentMarkingPosition = currentMarkingPosition
        self.markedNodeMap[self.currentMarkingPosition] = []

    def stopMarking(self) -> None:
        self.shouldMark = False
        self.currentMarkingPosition = 0

    def removeMarkedNodes(self) -> None:
        if self.markedNodeMap[self.currentMarkingPosition] is not None:
            self.markedNodeMap[self.currentMarkingPosition].sort(reverse=True)
            
            for nodeId in self.markedNodeMap[self.currentMarkingPosition]:
                self.removeNode(nodeId)
            
        self.clearMarkedNodeStack()
    
    def clearMarkedNodeStack(self) -> None:
        if (self.currentMarkingPosition in self.markedNodeMap):
            del self.markedNodeMap[self.currentMarkingPosition]  
        
      