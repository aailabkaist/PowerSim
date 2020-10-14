import sys

from SimulationEngine.ClassicDEVS.DEVSCoupledModel import DEVSCoupledModel
from SimulationEngine.CouplingGraph import CouplingEdge, CouplingNode

class DynamicDEVSCoupledModel(DEVSCoupledModel):

    def addCoupling(self, srcModel, srcPort, tarModel, tarPort):
        if srcModel.getModelID() + "(" + srcPort + ")" in self.nodesWithID:
            srcNode = self.nodesWithID[srcModel.getModelID() + "(" + srcPort + ")"]
        else:
            if isinstance(srcModel,DynamicDEVSCoupledModel):
                srcNode = CouplingNode(srcModel, srcModel.getModelID(), srcPort, blnDynamicDEVSCoupledModel=True)
            else:
                srcNode = CouplingNode(srcModel, srcModel.getModelID(), srcPort)
            self.nodesWithID[srcModel.getModelID() + "(" + srcPort + ")"] = srcNode

        if tarModel.getModelID() + "(" + tarPort + ")" in self.nodesWithID:
            tarNode = self.nodesWithID[tarModel.getModelID() + "(" + tarPort + ")"]
        else:
            if isinstance(tarModel,DynamicDEVSCoupledModel):
                tarNode = CouplingNode(tarModel, tarModel.getModelID(), tarPort, blnDynamicDEVSCoupledModel=True)
            else:
                tarNode = CouplingNode(tarModel, tarModel.getModelID(), tarPort)
            self.nodesWithID[tarModel.getModelID() + "(" + tarPort + ")"] = tarNode

        edge = CouplingEdge(srcNode, tarNode)
        self.edges.append(edge)
        if self.getSimulationEngine() != -1:
            self.getSimulationEngine().getCouplingGraph().addEdge(edge)


    def removeExternalOutputCoupling(self,srcModel,srcPort,tarPort):
        self.removeCoupling(srcModel, srcPort, self, tarPort)

    def removeExternalInputCoupling(self, srcPort, tarModel, tarPort):
        self.removeCoupling(self, srcPort, tarModel, tarPort)

    def removeInternalCoupling(self, srcModel, srcPort, tarModel, tarPort):
        self.removeCoupling(srcModel, srcPort, tarModel, tarPort)

    def removeCoupling(self, srcModel, srcPort, tarModel, tarPort):
        if srcModel.getModelID() + "(" + srcPort + ")" in self.nodesWithID.keys():
            srcNode = self.nodesWithID[srcModel.getModelID() + "(" + srcPort + ")"]
        else:
            return
        if tarModel.getModelID() + "(" + tarPort + ")" in self.nodesWithID.keys():
            tarNode = self.nodesWithID[tarModel.getModelID() + "(" + tarPort + ")"]
        else:
            return

        toRemove = -1
        for edge in self.edges:
            if srcNode == edge.srcNode and tarNode == edge.tarNode:
                toRemove = edge
                break
        if toRemove != -1:
            self.edges.remove(toRemove)
            self.getSimulationEngine().getCouplingGraph().removeEdge(toRemove)

    def funcStateTransition(self,strPort, event):
        pass

if __name__ == "__main__":
    pass