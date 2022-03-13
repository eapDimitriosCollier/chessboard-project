from Parser.Tree.Node import Node
from typing import Callable
from collections import deque

class ParseNode(Node):
    def __init__(self, nodeName: str = 'root', nodeInfo: dict = None) -> None:
        super().__init__(nodeName, nodeInfo)
        self.ASTNode = None
    
    def postOrderTraversal(self, func: Callable) -> None:
        root = self
        # TODO: Ένα καλό optimization θα ήταν η χρήση
        # iterative postOrderTraversal, αλλά αυτό χρειάζεται 
        # μόνο αν το δέντρο ξεπερνάει τα 1000 nodes σε βάθος
        # (δεν είναι ιδιαίτερα συχνό φαινόμενο.)
        # for node in self.nodes:
        #     node.postOrderTraversal(func)

        # func(currentNode)    
        if root is None:
            return
        
        # create an empty stack and push the root node
        stack = deque()
        stack.append(root)
    
        # create another stack to store postorder traversal
        out = deque()
        while stack:
            # pop a node from the stack and push the data into the output stack
            curr = stack.pop()
            out.append(curr)
            
            for node in curr.nodes:
                stack.append(node)
                
        while out:
            func(out.pop())        