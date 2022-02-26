from Parsing.Tree.Node import Node

class Tree:
    def __init__(self, rootNode=None) -> None:
        self.currentNode = rootNode
        self.rootNode = rootNode      

    def showTree(self) -> None:
        for node in self.rootNode.nodes:
            node.showNode()
            
    def insertNode(self, node: Node) -> None:
        assert(isinstance(node, Node))
        self.currentNode.nodes.append(node)
        node.nodeParent = self.currentNode
        self.currentNode = node

    def findNodeById(self, nodeId: int) -> Node:
        return self.rootNode.findNodeById(nodeId) 
        
    def removeNode(self, nodeId: int) -> None:
        nodeToRemove = self.findNodeById(nodeId)   
        nodeToRemove.nodeParent.nodes.remove(nodeToRemove)
