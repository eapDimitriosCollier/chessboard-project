class Node:
    count = 0
    
    def __init__(self, nodeName: str = 'root', nodeInfo: dict = None) -> None:
        Node.count+=1

        self.nodeName = nodeName
        self.nodeParent = None
        self.nodeInfo = nodeInfo
        self.nodes = []
        self.id = Node.count

    def showNode(self) -> None:
        print(f'{self.nodeParent.nodeName} -> {self.nodeName}')
        for node in self.nodes:
            node.showNode()
                
    def findNodeById(self, searchId: int) -> 'Node':
        if (self.id == searchId):
            return self
        
        for node in self.nodes:
            found = node.findNodeById(searchId) 
            if found:
                return found
            
    