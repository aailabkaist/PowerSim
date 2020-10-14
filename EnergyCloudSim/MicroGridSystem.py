from SimulationEngine.ClassicDEVS.DEVSCoupledModel import DEVSCoupledModel
from GridManagementSystem import GridManagementSystem
from Household import Household
from Messages import ESS_info
from ESS import ESS

import os
import numpy as np
import csv

b_Debug = False


def readHouseholdData(config):    
    #generates LD, LD_P, LD_Q of households
    LD_data_directory = os.path.join(config.getConfiguration('data_dir'), config.getConfiguration('LD csv'))
    LD_P_data_directory = os.path.join(config.getConfiguration('data_dir'), config.getConfiguration('LD_P csv'))
    LD_Q_data_directory = os.path.join(config.getConfiguration('data_dir'), config.getConfiguration('LD_Q csv'))
    #ESS_P_data_directory = os.path.join(config.getConfiguration('data_dir'), config.getConfiguration('ESS_P csv'))

    LD = np.loadtxt(LD_data_directory, skiprows=0, delimiter=',')    # (connectedBS, Phase)
    LD_P = np.loadtxt(LD_P_data_directory, skiprows=0, delimiter=',',encoding='utf-8-sig') # a time serise of active power (fix needed)
    LD_Q = np.loadtxt(LD_Q_data_directory, skiprows=0, delimiter=",",encoding='utf-8-sig') # a time serise of reactive power (fix needed)
    # if False:
    #     ESS_P = np.loadtxt(ESS_P_data_directory, skiprows=1, delimiter=",",encoding='utf-8-sig') # a time serise of ESS power (fix needed), now only for 10 cases
    #     ESS_Q = []
    # else:
    #     ESS_P = []
    #     ESS_Q = []
    # # not ready to consider EV and DG
    # ESS_P = []
    # ESS_Q = []    
    EV_P = []
    EV_Q = []
    DG_P = []
    DG_Q = []

    
    ret = []

    for i in range(len(LD)):
        temp = []
        temp.append(LD[i])   # add LD of ith household 
        temp.append(LD_P[i])
        temp.append(LD_Q[i])
        if len(EV_P) != 0:
            temp.append(EV_P[i])
            temp.append(EV_Q[i])
        if len(DG_P) != 0:
            temp.append(DG_P[i])
            temp.append(DG_Q[i])
        # if len(ESS_P) != 0:      #now add only 10 household
        #     try:
        #         temp.append(ESS_P[i])
        #     except:
        #         print('Household ',i+1,' does not have ESS')
        #     # temp.append(ESS_Q[i])

        ret.append(temp)
    
    return ret

def readESSdata(config):

    # ESS_data_file = config.getConfiguration('data_dir') + "/" + config.getConfiguration('ESS_P csv')
    ESS_P_data_directory = os.path.join(config.getConfiguration('data_dir'), config.getConfiguration('ESS_P csv'))
    print(ESS_P_data_directory)
    with open(ESS_P_data_directory, encoding='utf-8-sig') as f:    
        rdr = csv.reader(f)
        next(rdr,None)  # get rid of the header

        ret = []
    
        for line in rdr:            
            if b_Debug:
                print(line)    
            info = ESS_info(line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7],line[8],line[9])
            ret.append(info)

    return ret




class MicroGridSystem(DEVSCoupledModel):
    def __init__(self, objConfiguration):
        super().__init__("MicroGridSystem")
        
        # X,Y:  none

        # M   

        # generate GridStructure
        gridmanager = GridManagementSystem(objConfiguration)        
        self.addModel(gridmanager)
        
        # household: generate with LD, LD_P, LD_Q (ESS_P now removed)
        hh_initials = readHouseholdData(objConfiguration)
        
        # added by pietrok Household.Household_ID to 0
        Household.Household_ID = 0
        
        for hh_init in hh_initials:
            new_household = Household(hh_init)
            self.addModel(new_household)

            # Coupling Relations
            self.addInternalCoupling(gridmanager, "end", new_household, "end")
        
        # ESS initialize
        ESS_initials = readESSdata(objConfiguration)

        for ess_init in ESS_initials:
            new_ess = ESS(ess_init)
            # temporal output file generation
            for usage in ['totalE']:
                filename = os.path.join('result', new_ess.id + '_'+  usage +".csv")
                with open(filename, "w", encoding="utf-8", newline='') as ofile:
                    ofile.write("time,charge,discharge,storage\n")
            self.addModel(new_ess)

            # print(new_ess.info.LD)
            # print(new_ess.info.LD_num)
            # print(new_ess.info.Household)
            # print(new_ess.info.power)
            # print(new_ess.info.charge_start)
            # print(new_ess.info.charge_end)

            self.addInternalCoupling(gridmanager, "end", new_household, "end")










        
            


        

        
        
    
