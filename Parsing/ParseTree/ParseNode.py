from Parsing.Tree.Node import Node
from typing import Callable

class ParseNode(Node):
    def __init__(self, nodeName: str = 'root', nodeInfo: dict = None) -> None:
        super().__init__(nodeName, nodeInfo)
        self.ASTNode = None
    
    def postOrderTraversal(self, func: Callable) -> None:
        currentNode = self
        for node in self.nodes:
            node.postOrderTraversal(func)

        func(currentNode)    