import sys

from SimulationEngine.ClassicDEVS.DEVSCoupledModel import DEVSCoupledModel
from SimulationEngine.CouplingGraph import *
from SimulationEngine.Utility.Logger import Logger
from SimulationEngine.Visualzer.Visualizer import Visualizer
from SimulationEngine.Utility.Event import *

class SimulationEngine:

    def __init__(self):
        self.infiniteTime = 10000000000
        self.models = []
        self.queueEvent = []
        self.visualNodes = []
        self.visualEdges = []

    def setOutmostModel(self,model):
        self.model = model
        self.models.append(model)
        self.couplingGraph = CouplingGraph(self)

        modelBFS = [model]
        while len(modelBFS) != 0:
            currentModel = modelBFS.pop(0)
            if isinstance(currentModel,DEVSCoupledModel) == True:
                children = currentModel.getModels()
                for childModelID in children:
                    children[childModelID].setSimulationEngine(self)
                    modelBFS.append(children[childModelID])
                    self.models.append(children[childModelID])

                nodes = currentModel.getCouplingNodes()
                edges = currentModel.getCouplingEdges()
                for nodeID in nodes:
                    self.couplingGraph.addNode(nodes[nodeID])
                for edge in edges:
                    self.couplingGraph.addEdge(edge)

    def addEvent(self,event):
        self.queueEvent.append(event)

    def run(self,maxTime = -1,ta=-1,visualizer=False,logFileName=-1,logGeneral=False,logActivateState=False,logActivateMessage=False,logActivateTA=False,logStructure=False):
        self.maxTime = maxTime
        self.ta = ta
        self.logger = Logger(self,logFileName,logGeneral,logActivateState,logActivateMessage,logActivateTA,logStructure)

        self.runInitialize()
        if visualizer == True:
            self.runWithVisualizer()
        else:
            self.runWithoutVisualizer()

    def runWithVisualizer(self):
        self.minTA = 0
        if self.maxTime <= 0:
            self.maxTime = 10000
        self.visualizer = Visualizer(self,self.maxTime)

    def runWithoutVisualizer(self):
        self.minTA = 0
        while self.minTA < self.infiniteTime and self.currentTime < self.maxTime:
            #print("!!! 1:"+str(self.currentTime)+","+str(self.maxTime))
            #print("!!! 2:"+str(self.minTA)+","+str(self.infiniteTime))
            self.runSingleStep()

    def runInitialize(self):
        self.currentTime = 0
        for model in self.models:
            model.setLogger(self.logger)
            if isinstance(model,DEVSAtomicModel) == True:
                model.setTime(self.currentTime)
                model.execTimeAdvance()
    
    def runInitializeForExternal(self, maxTime = -1, ta=-1, logFileName=-1, logGeneral=False,logActivateState=False,logActivateMessage=False,logActivateTA=False,logStructure=False):
        self.maxTime = maxTime
        self.ta = ta;
        self.logger =  Logger(self,logFileName,logGeneral,logActivateState,logActivateMessage,logActivateTA,logStructure)

        self.runInitialize()

    def runSingleStep(self):
        self.logger.log(Logger.GENERAL, "-------------------------------------------")
        self.logger.log(Logger.GENERAL, "Simulation Time : " + str(self.currentTime))
        self.logger.log(Logger.GENERAL, "-------------------------------------------")

        self.visualNodes = []
        self.visualEdges = []
        for model in self.models:
            self.logger.log(Logger.STATE, model.getModelID() + " : " + str(model.getStates()))
            for visualNode in model.getVisualNodes():
                self.visualNodes.append(visualNode)
            for visualEdge in model.getVisualEdges():
                self.visualEdges.append(visualEdge)

        for event in self.queueEvent:
            self.logger.log(Logger.MESSAGE,
                            event.getSenderModel().getModelID() + "(" + event.getSenderPort() + ")" + ":" + str(
                                event.getMessage()))

        if len(self.queueEvent) == 0:
            self.minTA = self.model.queryTime() #.queryMinTimeAdvance()
            #print("!!! ENGINE : Min TA Check : "+str(self.minTA))
            if self.minTA > self.infiniteTime: #== sys.float_info.max or self.minTA > 10000:
                self.logger.log(Logger.GENERAL, "Terminate by finding the minimum time advance as infinite\n")
                return
            if self.ta != -1:
                self.minTA = self.ta
            self.currentTime = self.minTA # self.currentTime + self.minTA
            self.model.performTimeAdvance(self.currentTime)
        else:
            while len(self.queueEvent) != 0:
                idxToPop = 0
                for itr in range(len(self.queueEvent)):
                    if isinstance(self.queueEvent[idxToPop],ResolutionEvent) == True:
                        if isinstance(self.queueEvent[itr],RecursionError) == False:
                            idxToPop = itr
                event = self.queueEvent.pop(idxToPop)
                self.couplingGraph.broadcastEvent(event)

    def getTime(self):
        return self.currentTime

    def getVisualNodes(self):
        return self.visualNodes

    def getVisualEdges(self):
        return self.visualEdges

    def getCouplingGraph(self):
        return self.couplingGraph

if __name__ == "__main__":
    pass
