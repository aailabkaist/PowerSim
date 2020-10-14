import sys
from SimulationEngine.ClassicDEVS.DEVSModel import DEVSModel
from SimulationEngine.Utility.Event import Event, ResolutionEvent
from SimulationEngine.Utility.Logger import Logger
from SimulationEngine.ClassicDEVS.DEVSAtomicModel import DEVSAtomicModel

class MRDEVSAtomicModel(DEVSAtomicModel):

    def __init__(self,ID,activated=True):
        super().__init__(ID)
        self.activated = activated
        self.statesResolution = {}

    def getResolutionStateValue(self,varState):
        return self.statesResolution[varState]

    def setResolutionStateValue(self,varState,varStateValue,blnNoEvent = False):
        if self.statesResolution[varState] != varStateValue:
            self.statesResolution[varState] = varStateValue
            if blnNoEvent == False:
                eventResolutionChange = ResolutionEvent(self, [varState,varStateValue])
                if eventResolutionChange in self.engine.queueEvent:
                    pass
                else:
                    self.engine.addEvent(eventResolutionChange)

    def addResolutionStateVariable(self, varState, varStateValue):
        self.statesResolution[varState] = varStateValue

    def setActivate(self,activated):
        self.activated = activated
        if self.activated == True:
            self.execTimeAdvance()

    def getActivate(self):
        return self.activated

    def receiveExternalEvent(self,event):
        if self.activated == True:
            super().receiveExternalEvent(event)

    def performTimeAdvance(self,currentTime):
        if self.activated == True:
            super().performTimeAdvance(currentTime)
            self.funcResolutionTransition()

    def queryTimeAdvance(self):
        if self.activated == True:
            self.logger.log(Logger.TA,"Query MIN TA ("+self.getModelID()+") : " + str(self.nextTimeAdvance))
            return self.nextTimeAdvance
        else:
            return sys.float_info.max

    def queryTime(self):
        if self.activated == True:
            self.logger.log(Logger.TA,"Query Time ("+self.getModelID()+") : " + str(self.nextTime))
            return self.nextTime
        else:
            return sys.float_info.max

    def funcResolutionTransition(self):
        pass


if __name__ == "__main__":
    pass