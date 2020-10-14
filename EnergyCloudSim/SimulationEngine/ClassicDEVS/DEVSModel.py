from SimulationEngine.Visualzer.Visualizer import VisualNode, VisualEdge

class DEVSModel:

    engine = -1

    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.states = {}
        self.visualNodes = []
        self.visualEdges = []
        self.containerModel = None

    def setContainerModel(self,model):
        self.containerModel = model

    def getContainerModel(self):
        return self.containerModel

    def setModelID(self, ID):
        self.ID = ID

    def getModelID(self):
        return self.ID

    def addInputPort(self,varInput):
        self.inputs.append(varInput)

    def addOutputPort(self, varOutput):
        self.outputs.append(varOutput)

    def addStateVariable(self, varState, varStateValue):
        self.states[varState] = varStateValue

    def removeInputPort(self, varInput):
        self.inputs.remove(varInput)

    def removeOutputPort(self, varOutput):
        self.outputs.remove(varOutput)

    def removeStateVariable(self, varState):
        self.states.remove(varState)

    def getInputPorts(self):
        return self.inputs

    def getOutputPorts(self):
        return self.outputs

    def getStates(self):
        return self.states

    def getStateValue(self,varState):
        return self.states[varState]

    def setStateValue(self,varState,varStateValue):
        self.states[varState] = varStateValue

    def setSimulationEngine(self, engine):
        self.engine = engine

    def getSimulationEngine(self):
        return self.engine

    def setModelID(self, ID):
        self.ID = ID

    def getModelID(self):
        return self.ID

    def getModelID(self):
        return self.ID

    def getTime(self):
        return self.engine.getTime()

    def setTime(self,currentTime):
        self.time = currentTime

    def setLogger(self,logger):
        self.logger = logger

    def addVisualizeNode(self,name,x,y,size,color):
        self.visualNodes = [VisualNode(name,x,y,size,color)]

    def addVisualizeEdge(self, srcName, tarName):
        self.visualEdges = [VisualEdge(srcName,tarName)]

    def getVisualNodes(self):
        return self.visualNodes

    def getVisualEdges(self):
        return self.visualEdges

    def removeVisualNodes(self):
        self.visualNodes = []

    def removeVisualEdges(self):
        self.visualEdges = []

if __name__ == "__main__":
    pass