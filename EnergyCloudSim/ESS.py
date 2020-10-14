from SimulationEngine.ClassicDEVS.DEVSAtomicModel import DEVSAtomicModel
from GridStructure import GridStructure
from Messages import ESS_info

import math


b_Debug = False

class ESS(DEVSAtomicModel):

    def __init__(self, ess_info):
        if b_Debug:
            ess_info.to_string()

        self.grid = GridStructure()

        self.id = str("ESS_" + str(ess_info.id))      
        super().__init__(self.id)

        self.info = ess_info
        self.grid.registerESS(ess_info)

        #DEVS X, Y, S
        self.addInputPort("end")
        self.setStateValue("state","READY") # READY, CHARGE, DISCHARGE, UPDATE, END

    def funcExternalTransition(self, strPort, objEvent):
    
        if strPort == "end":
            self.setStateValue("state", "END")

    def funcInternalTransition(self):
    
        if self.getStateValue("state") == "READY":            
            if float(self.info.charge_start) <= self.time and self.time <= float(self.info.charge_end):
                self.setStateValue("state", "CHARGE")
            else:
                self.setStateValue("state", "DISCHARGE")                           
            
        elif self.getStateValue("state") == "CHARGE":
            self.updateESSInfo(True)
            self.setStateValue("state", "UPDATE")

        elif self.getStateValue("state") == "DISCHARGE":
            self.updateESSInfo(False)
            self.setStateValue("state", "UPDATE")
        
        elif self.getStateValue("state") == "UPDATE":
            self.setStateValue("state", "READY")             
            
    def funcOutput(self):
        pass    
            
    def funcTimeAdvance(self):
                            
        if self.getStateValue("state") == "READY":
            return 0.2

        elif self.getStateValue("state") == "CHARGE":
            return 0.2

        elif self.getStateValue("state") == "DISCHARGE":
            return 0.2
        elif self.getStateValue("state") == "UPDATE":
            return 0.6
        elif self.getStateValue("state") == "END":
            return math.inf

    def updateESSInfo(self,bCharge):
        # calculate Energy state changes for previous P: currentP: + --> charge, - --> discharge
        # 1) charge case

        # if self.info.currentP != 0:
        #     print('id', self.id)
        #     print('currentP',self.info.currentP)
        #     print('CurrentEnergy',self.info.currentEnergy)
        #     print('capacity',self.info.capacity)

        if self.info.currentP > 0:  # charge case (with the efficiency)
            self.info.currentEnergy += self.info.currentP / 60 * float(self.info.efficiency) * 0.01 # hour to min
            if self.info.currentEnergy > float(self.info.capacity):
                self.info.currentEnergy = float(self.info.capacity)            
        elif self.info.currentEnergy > 0 and self.info.currentP < 0:   # discharge case
            self.info.currentEnergy += self.info.currentP / 60
            if self.info.currentEnergy < 0:
                self.info.currentEnergy = 0



        # update currentP
        if bCharge:
            self.info.currentP = float(self.info.power)
        else:
            if self.info.currentEnergy != 0:
                self.info.currentP = -1 * float(self.info.power)
            else:
                self.info.currentP = 0