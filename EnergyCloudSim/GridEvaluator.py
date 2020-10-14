from SimulationEngine.ClassicDEVS.DEVSAtomicModel import DEVSAtomicModel
from GridStructure import GridStructure
from Messages import ReportMsg

import random
import math

class GridEvaluator(DEVSAtomicModel):
    def __init__(self, strID):
        super().__init__(strID)
        #self.name = "GridEvaluator"
        self.grid = GridStructure()

        # DEVS X, Y, S
        self.addInputPort("end")
        self.addOutputPort("report")
        
        self.setStateValue("state", "WAIT")   # WAIT, CALCULATE, END
    
    def writeResult(self):
        #add outputfile (to be filled)
        print("write calculation results at time: %f" % self.time)
        return

    def funcExternalTransition(self, strPort, objEvent): 
        if strPort == "END":
            self.setStateValue("state", "END")
    
    def funcInternalTransition(self):
    
        if self.getStateValue("state") == "WAIT":
            self.setStateValue("state", "CALCULATE")        
        
    def funcOutput(self):
        if self.getStateValue("state") == "CALCULATE" or "WAIT":
            # do some calculation on GridStructure
            I_flow, V, Sinj, pf_flag = self.grid.analyzePowerFlow()
            # do calculation for the metrics
            self.grid.calculateHouseholdVoltage(V)
            self.grid.calculateTransformerPower(I_flow,V,Sinj)
            self.grid.calculateTransformerCurrent(I_flow)       

            res = ReportMsg()
            self.addOutputEvent("report", res)

        return
    
    def funcTimeAdvance(self):                    
        if self.getStateValue("state") == "WAIT":
            return 0.7

        elif self.getStateValue("state") == "CALCULATE":
            return 1

        elif self.getStateValue("state") == "END":
            return math.inf





         