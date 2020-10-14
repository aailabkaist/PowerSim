from SimulationEngine.Utility.Logger import Logger
from SimulationEngine.MRDEVS.MRDEVSAtomicModel import DEVSAtomicModel, MRDEVSAtomicModel

class CouplingGraph:

    def __init__(self,engine):
        self.engine = engine
        self.edges = []
        self.nodes = []
        self.adjacentNodes = {}
        self.nodesWithID = {}

    def addNode(self,node):
        if (str(node) in self.nodesWithID) == False:
            self.nodes.append(node)
            self.nodesWithID[str(node)] = node
            self.adjacentNodes[str(node)] = []

    def addEdge(self,edge):
        srcNode = edge.getSrcNode()
        tarNode = edge.getTarNode()
        self.addNode(srcNode)
        self.addNode(tarNode)
        self.edges.append(edge)
        self.adjacentNodes[str(srcNode)].append(str(tarNode))

    def removeEdge(self,edge):
        srcNode = edge.getSrcNode()
        tarNode = edge.getTarNode()
        if str(tarNode) in self.adjacentNodes[str(srcNode)]:
            self.adjacentNodes[str(srcNode)].remove(str(tarNode))
        toRemove = -1
        for edge in self.edges:
            if edge.getSrcNode() == srcNode and edge.getTarNode() == tarNode:
                toRemove = edge
                break
        if toRemove != -1:
            self.edges.remove(toRemove)

    def getTerminalNodesInPath(self,srcNode,event):
        adjacentNodes = self.adjacentNodes[str(srcNode)]
        ret = []
        if len(adjacentNodes) == 0:
            return [srcNode]
        for nodeID in adjacentNodes:
            if nodeID in self.nodesWithID:
                node = self.nodesWithID[nodeID]
                if node.getDynamicDEVSCoupledModel() == True:
                    node.getModel().funcStateTransition(node.getPort(),event.getMessage())
                ret = ret + self.getTerminalNodesInPath(node,event)
        return ret

    def broadcastEvent(self,event):
        if event.getResolutionChange() == False:
            #self.printOut()
            srcModel = event.getSenderModel()
            srcPort = event.getSenderPort()
            srcNode = self.nodesWithID[srcModel.getModelID()+"("+srcPort+")"]
            tarNodes = self.getTerminalNodesInPath(srcNode,event)
            if srcNode in tarNodes:
                tarNodes.remove(srcNode)
            self.engine.logger.log(Logger.MESSAGE, str(event.getMessage()) + "," + srcModel.getModelID() + "(" + srcPort + "), # Target Model : "+str(len(tarNodes)))
            for tarNode in tarNodes:
                tarModel = tarNode.getModel()
                self.engine.logger.log(Logger.MESSAGE,str(event.getMessage())+","+srcModel.getModelID()+"("+srcPort+")"+"-->"+tarModel.getModelID()+"("+tarNode.getPort()+")")
                if isinstance(tarModel,DEVSAtomicModel):
                    #tarModel.funcExternalTransition(tarNode.getPort(),event.getMessage())
                    tarModel.receiveExternalEvent(tarNode.getPort(),event.getMessage(),self.engine.getTime())
                    if tarModel.checkContinue() == False:
                        tarModel.execTimeAdvance()
                    if isinstance(tarModel,MRDEVSAtomicModel):
                        tarModel.funcResolutionTransition()

        if event.getResolutionChange() == True:
            currentModel = event.getSenderModel()
            parentModel = currentModel.getContainerModel()
            if parentModel == None:
                return
            oldState = parentModel.getResolutionState()
            if oldState == None:
                return
            oldStructure = parentModel.getResolutionStructureInfo(oldState)
            parentModel.funcResolutionTransition(event,oldStructure.getActivatedModels())
            if oldState != parentModel.getResolutionState():
                currentState = parentModel.getResolutionState()
                currentStructure = parentModel.getResolutionStructureInfo(currentState)
                parentModel.funcStateTranslation(currentState,oldStructure.getActivatedModels(),currentStructure.getActivatedModels())
                for models in currentStructure.getActivatedModels():
                    models.setActivate(True)

    def printOut(self):
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")
        self.engine.logger.log(Logger.STRUCTURE,"Coupling Nodes")
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")
        for node in self.nodes:
            self.engine.logger.log(Logger.STRUCTURE,node.getModelID()+"("+node.getPort()+")"+",DynamicCoupling : "+str(node.getDynamicDEVSCoupledModel()))
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")
        self.engine.logger.log(Logger.STRUCTURE,"Coupling Edges")
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")
        for edge in self.edges:
            output = edge.getSrcNode().getModelID()+"("+edge.getSrcNode().getPort()+")"
            output = output + "-->" + edge.getTarNode().getModelID() + "(" + edge.getTarNode().getPort() + ")"
            self.engine.logger.log(Logger.STRUCTURE,output)
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")
        self.engine.logger.log(Logger.STRUCTURE,"Coupling Adjacent Nodes")
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")
        for key in self.adjacentNodes:
            self.engine.logger.log(Logger.STRUCTURE,key + " : " +str(self.adjacentNodes[key]))
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")

class CouplingEdge:

    def __init__(self,srcNode,tarNode):
        self.srcNode = srcNode
        self.tarNode = tarNode

    def getSrcNode(self):
        return self.srcNode

    def getTarNode(self):
        return self.tarNode

    def __str__(self):
        return str(self.srcNode)+"-->"+str(self.tarNode)

class CouplingNode:

    def __init__(self,model,modelID,port,blnDynamicDEVSCoupledModel=False,blnMRDEVSCoupledModel=False):
        self.modelID = modelID
        self.port = port
        self.model = model
        self.blnDynamicDEVSCoupledModel = blnDynamicDEVSCoupledModel
        self.blnMRDEVSCoupledModel = blnMRDEVSCoupledModel

    def equal(self,node):
        if self.modelID == node.modelID and self.port == node.port:
            return True
        return False

    def getPort(self):
        return self.port

    def getModelID(self):
        return self.modelID

    def getModel(self):
        return self.model

    def getMRDEVSCoupledModel(self):
        return self.blnMRDEVSCoupledModel

    def getDynamicDEVSCoupledModel(self):
        return self.blnDynamicDEVSCoupledModel

    def __str__(self):
        return self.modelID+"("+self.port+")"

if __name__ == "__main__":
    pass

