from SimulationEngine.ClassicDEVS.DEVSAtomicModel import DEVSAtomicModel
from GridStructure import GridStructure
from Messages import Household_info

import math


b_Debug = False

class Household(DEVSAtomicModel):
    Household_ID = 0

    def __init__(self, hh_init):        
        self.id = str("Household_" + str(Household.Household_ID))      
        super().__init__(self.id)

        # add more individual attributes
        self.info = Household_info(Household.Household_ID, hh_init[0])
        Household.Household_ID += 1
        
        if b_Debug == True:
            self.info.toString()

        self.grid = GridStructure()        
        self.grid.registerHousehold(self.info)        
        # self.connectedBS = hh_info[0][0]
        # self.connectedPhase = hh_info[0][1] # 1, 2, 3

        # (temporary) a list of LDs at 1440 times
        self.LD_P = hh_init[1]
        self.LD_Q = hh_init[2]
        
        # (temporary) EV and DG info (to be added)
        if len(hh_init) > 5:
            self.EV_P = hh_init[3]
            self.EV_Q = hh_init[4]
        if len(hh_init) > 7:
            self.DG_P = hh_init[3]
            self.DG_Q = hh_init[4]

        # (temporary) ESS info (to be modified)
        if len(hh_init) > 3:
            self.ESS_P = hh_init[3]


        #DEVS X, Y, S
        self.addInputPort("end")        
        
        self.setStateValue("state", "WAIT") # WAIT, UPDATE, END
        

    def funcExternalTransition(self, strPort, objEvent):
    
        if strPort == "end":
            self.setStateValue("state", "END")

    def funcInternalTransition(self):
    
        if self.getStateValue("state") == "WAIT":
            self.setStateValue("state", "UPDATE")
            self.updateLD()

        elif self.getStateValue("state") == "UPDATE":
            self.setStateValue("state", "UPDATE")
            self.updateLD()
    
    def funcOutput(self):
    
        if self.getStateValue("state") == "UPDATE":
            return            
            
    def funcTimeAdvance(self):
                            
        if self.getStateValue("state") == "WAIT":
            return 0.4

        elif self.getStateValue("state") == "UPDATE":
            return 1

        elif self.getStateValue("state") == "END":
            return math.inf

    def updateLD(self):
        # at this time, LD_P and LD_Q only
        #print("Update %s at time %f"% (self.id, self.time))
        self.info.LD_P = self.LD_P[int(self.time)]
        self.info.LD_Q = self.LD_Q[int(self.time)]
        # try:
        #     self.info.ESS_P = self.ESS_P[int(self.time)]
        # except:
        #     pass


    

