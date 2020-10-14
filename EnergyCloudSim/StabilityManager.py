from SimulationEngine.ClassicDEVS.DEVSAtomicModel import DEVSAtomicModel
from GridStructure import GridStructure
from Messages import *

import numpy as np
import random
import math

bDebug = False

class StabilityManager(DEVSAtomicModel):
    def __init__(self, strID, config):
        super().__init__(strID)           
        self.bEnd = False
        self.endtime = float(config.getConfiguration("end time"))
        self.grid = GridStructure()

        # X, Y, S
        self.addInputPort("report") 
        self.addOutputPort("end")            
        self.setStateValue("state", "WAIT")   # WAIT, STABILITY_CHECK, END_CONDITION_CHECK, END
    
    def checkEndCondition(self):
        if self.endtime < self.time:
            self.bEnd = True
        
        return

    def funcExternalTransition(self, strPort, objEvent): 
        if strPort == "report" and self.getStateValue("state") == "WAIT":
            self.setStateValue("state", "STABILITY_CHECK")

            # do calculation for the metrics
            print("at time:", round(self.time) ,"Calculation in StabilityManager")
            self.grid.check_stability_power()
            customer_list,unstable_percent = self.grid.check_stability_voltage()
            
            if bDebug:
                #print("at time: ", self.time ,"Calculation in GridEvaluator of ",unstable_percent,"% with",customer_list)
                print("at time: ", round(self.time) ,"Calculation in StabilityManager of ",unstable_percent,"%")
                print("Check current Stability in Stability Manager:",self.grid.power_imbalance)
            
            # record output at every tick
            self.grid.writeResults(round(self.time))            
            
    
    def funcInternalTransition(self):
    
        if self.getStateValue("state") == "WAIT":
            self.setStateValue("state", "STABILITY_CHECK")

        elif self.getStateValue("state") == "STABILITY_CHECK":
            self.setStateValue("state", "END_CONDITION_CHECK")
            # check the stability: voltage and power
            # self.grid.check_stability_voltage()

        
        elif self.getStateValue("state") == "END_CONDITION_CHECK":
            self.setStateValue("state", "WAIT")        

    
    def funcOutput(self):
        if self.bEnd == True:
           end = EndMsg()
           self.addOutputEvent("end", end)
        self.checkEndCondition()
                
    def funcTimeAdvance(self):
                    
        if self.getStateValue("state") == "WAIT":
            return math.inf

        elif self.getStateValue("state") == "END_CONDITION_CHECK":
            return 0.1

        elif self.getStateValue("state") == "STABILITY_CHECK":
            return 0.2

        elif self.getStateValue("state") == "END":
            return math.inf
    

        
