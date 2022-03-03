from Parser.Tree.Node import Node
from typing import Callable

class ParseNode(Node):
    def __init__(self, nodeName: str = 'root', nodeInfo: dict = None) -> None:
        super().__init__(nodeName, nodeInfo)
        self.ASTNode = None
    
    def postOrderTraversal(self, func: Callable) -> None:
        currentNode = self
        # TODO: Ένα καλό optimization θα ήταν η χρήση
        # iterative postOrderTraversal, αλλά αυτό χρειάζεται 
        # μόνο αν το δέντρο ξεπερνάει τα 1000 nodes σε βάθος
        # (δεν είναι ιδιαίτερα συχνό φαινόμενο.)
        for node in self.nodes:
            node.postOrderTraversal(func)

        func(currentNode)    