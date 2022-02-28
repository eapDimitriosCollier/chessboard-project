from Parser.Tree.Node import Node

class Tree:
    def __init__(self) -> None:
        self.currentNode = None
        self.rootNode = None      

    def showTree(self) -> None:
        for node in self.rootNode.nodes:
            node.showNode()
            
    def insertNode(self, node: Node) -> None:
        assert(isinstance(node, Node))
        if self.rootNode is None:
            self.rootNode = node
        else:
            self.currentNode.nodes.append(node)
            node.nodeParent = self.currentNode
            
        self.currentNode = node

    def findNodeById(self, nodeId: int) -> Node:
        return self.rootNode.findNodeById(nodeId) 
        
    def removeNode(self, nodeId: int) -> None:
        nodeToRemove = self.findNodeById(nodeId)   
        nodeToRemove.nodeParent.nodes.remove(nodeToRemove)
