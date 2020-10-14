import sys

from SimulationEngine.ClassicDEVS.DEVSCoupledModel import DEVSCoupledModel
from SimulationEngine.DynamicDEVS.DynamicDEVSCoupledModel import DynamicDEVSCoupledModel
from SimulationEngine.Utility.Logger import Logger
from SimulationEngine.Utility.Event import *

class MRDEVSCoupledModel(DynamicDEVSCoupledModel):

    def __init__(self, ID):
        super().__init__(ID)
        self.activate = True
        self.resolutionInfos = {}
        self.stateResolution = None

    def getResolutionStructureInfo(self,strState):
        return self.resolutionInfos[strState]

    def addResolutionStructureInfo(self,strState,actiavtedModels,deactivatedModels,couplingsToAdd,couplingsToRemove):
        self.resolutionInfos[strState] = ResolutionModelStructure(actiavtedModels,deactivatedModels,couplingsToAdd,couplingsToRemove)

    def getResolutionState(self):
        return self.stateResolution

    def setResolutionState(self, strState, blnNoEvent = False):
        if self.stateResolution != strState:
            self.stateResolution = strState
            info = self.resolutionInfos[strState]

            for models in info.getActivatedModels():
                models.setActivate(True)
            for models in info.getDeactivatedModels():
                models.setActivate(False)
            for coupling in info.getCouplingsToAdd():
                self.addCoupling(coupling['srcModel'],coupling['srcPort'],coupling['tarModel'],coupling['tarPort'])
            for coupling in info.getCouplingsToRemove():
                self.removeCoupling(coupling['srcModel'], coupling['srcPort'], coupling['tarModel'], coupling['tarPort'])

            if blnNoEvent == False:
                eventResolutionChange = ResolutionEvent(self, ['ResolutionState', strState])
                if eventResolutionChange in self.engine.queueEvent:
                    pass
                else:
                    self.engine.addEvent(eventResolutionChange)

    def setActivate(self,activated):
        self.activate = activated

    def getActivate(self):
        return self.activate

    def queryMinTimeAdvance(self):
        if self.activate == True:
            minTA = sys.float_info.max
            for modelID in self.models:
                model = self.models[modelID]
                ta = model.queryTimeAdvance()
                if ta < minTA:
                    minTA = ta
            self.logger.log(Logger.TA,"Query MIN TA (" + self.getModelID() + ") : " + str(minTA))
            return minTA
        else:
            return sys.float_info.max

    def queryMinTime(self):
        if self.activate == True:
            nextTime = sys.float_info.max
            for modelID in self.models:
                model = self.models[modelID]
                time = model.queryTime()
                if time < nextTime:
                    nextTime = time
            self.logger.log(Logger.TA,"Query Min Time (" + self.getModelID() + ") : " + str(nextTime))
            return nextTime
        else:
            return sys.float_info.max

    def performTimeAdvance(self,currentTime):
        if self.activate == True:
            self.time = currentTime
            for modelID in self.models:
                modelNextTime = self.models[modelID].queryTime()
                if modelNextTime <= currentTime:
                    self.models[modelID].performTimeAdvance(currentTime)

    def queryTimeAdvance(self):
        if self.activate == True:
            return self.queryMinTimeAdvance()
        else:
            return sys.float_info.max

    def queryTime(self):
        if self.activate == True:
            return self.queryMinTime()
        else:
            return sys.float_info.max

    def funcResolutionTransition(self,event):
        pass

    def funcStateTranslation(self,strCurrentState,lstDeactivatedModels,lstActivatedModels):
        pass

class ResolutionModelStructure:

    def __init__(self,actiavtedModels,deactivatedModels,couplingsToAdd,couplingsToRemove):
        self.activatedModels = actiavtedModels
        self.deactivatedModels = deactivatedModels
        self.couplingsToAdd = couplingsToAdd
        self.couplingsToRemove = couplingsToRemove

    def getActivatedModels(self):
        return self.activatedModels

    def getDeactivatedModels(self):
        return self.deactivatedModels

    def getCouplingsToAdd(self):
        return self.couplingsToAdd

    def getCouplingsToRemove(self):
        return self.couplingsToRemove

if __name__ == "__main__":
    pass